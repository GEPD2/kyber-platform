"""
Leaderboard router — /api/leaderboard/*

IMPORTANT: FastAPI matches routes in declaration order.
/global must come BEFORE /{mode} so it is not swallowed as a path parameter.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps     import get_current_user
from app.models.models import Leaderboard, User
from app.services.challenge_store import VALID_MODES

router = APIRouter()


@router.get("/global")
async def leaderboard_global(
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    """
    Aggregate best_score across all modes per user, return top 20.
    Declared first so FastAPI does not treat 'global' as a {mode} value.
    """
    result = await db.execute(
        select(
            User.username,
            func.sum(Leaderboard.best_score).label("total_score"),
            func.sum(Leaderboard.total_correct).label("total_correct"),
            func.sum(Leaderboard.total_attempts).label("total_attempts"),
            func.max(Leaderboard.best_streak).label("best_streak"),
        )
        .join(Leaderboard, User.id == Leaderboard.user_id)
        .group_by(User.id, User.username)
        .order_by(desc("total_score"))
        .limit(20)
    )
    rows = result.all()
    return [
        {
            "rank":           i + 1,
            "username":       r.username,
            "total_score":    r.total_score    or 0,
            "total_correct":  r.total_correct  or 0,
            "total_attempts": r.total_attempts or 0,
            "best_streak":    r.best_streak    or 0,
        }
        for i, r in enumerate(rows)
    ]


@router.get("/{mode}")
async def leaderboard_by_mode(
    mode: str,
    db:   AsyncSession = Depends(get_db),
    _:    User = Depends(get_current_user),
):
    """Top-20 players for a single difficulty mode."""
    if mode not in VALID_MODES:
        raise HTTPException(status_code=404, detail=f"Mode '{mode}' not found.")

    result = await db.execute(
        select(Leaderboard, User.username)
        .join(User, Leaderboard.user_id == User.id)
        .where(Leaderboard.mode == mode)
        .order_by(desc(Leaderboard.best_score))
        .limit(20)
    )
    rows = result.all()
    return [
        {
            "rank":          i + 1,
            "username":      username,
            "best_score":    lb.best_score,
            "correct":       lb.total_correct,
            "attempts":      lb.total_attempts,
            "best_streak":   lb.best_streak,
            "updated_at":    lb.updated_at.isoformat() if lb.updated_at else None,
        }
        for i, (lb, username) in enumerate(rows)
    ]
