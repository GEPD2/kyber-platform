"""
Users router — /api/users/*

Routes:
  GET /api/users/me              — own profile + aggregated stats
  PUT /api/users/me/password     — change password (CSRF required)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps     import get_current_user, require_csrf
from app.core.security import hash_password, verify_password
from app.models.models import Leaderboard, User

router = APIRouter()


# Schemas

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if len(v) > 128:
            raise ValueError("Password too long.")
        return v


# Endpoints

@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    """Return own profile and aggregated score statistics across all modes."""
    result = await db.execute(
        select(Leaderboard).where(Leaderboard.user_id == user.id)
    )
    lb_rows = result.scalars().all()

    return {
        "id":         user.id,
        "username":   user.username,
        "email":      user.email,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_admin":   user.is_admin,
        "stats": {
            "total_score":    sum(r.best_score     for r in lb_rows),
            "total_correct":  sum(r.total_correct  for r in lb_rows),
            "total_attempts": sum(r.total_attempts for r in lb_rows),
            "modes_played":   len(lb_rows),
        },
        "mode_scores": {
            r.mode: {
                "best_score":  r.best_score,
                "correct":     r.total_correct,
                "attempts":    r.total_attempts,
                "best_streak": r.best_streak,
                "updated_at":  r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in lb_rows
        },
    }


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body:  ChangePasswordRequest,
    _csrf: None = Depends(require_csrf),
    user:  User = Depends(get_current_user),
    db:    AsyncSession = Depends(get_db),
):
    """Change own password. Requires current password + valid CSRF token."""
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    user.password_hash = hash_password(body.new_password)
    await db.flush()
