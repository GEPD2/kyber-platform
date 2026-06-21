"""
Challenges router, /api/challenges/*

IMPORTANT: FastAPI matches routes in declaration order.
/submit and /progress/* must come BEFORE /{mode} to avoid being swallowed
as path-parameter values.

Routes:
  POST /api/challenges/submit, validate answer, record submission
  GET  /api/challenges/progress/{mode}, user's answered questions for a mode
  GET  /api/challenges/{mode}, question metadata (no correct answers)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, field_validator
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps     import get_current_user, require_csrf
from app.core.security import sanitise_answer, verify_session_cookie
from app.models.models import Leaderboard, Submission, User
from app.services.answer_validator import validate_answer
from app.services.challenge_store  import ANSWER_KEYS, VALID_MODES, get_challenge, get_mode_meta

router = APIRouter()


# Schemas

class SubmitRequest(BaseModel):
    mode:        str
    question_id: int
    answer:      str    # option index string (btns), value string (duo), JSON array (gaps)
    streak:      int = 0

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in VALID_MODES:
            raise ValueError(f"Invalid mode '{v}'.")
        return v

    @field_validator("answer")
    @classmethod
    def clean_answer(cls, v: str) -> str:
        # sanitise_answer: strips null bytes, limits length, blocks path traversal + XXE
        return sanitise_answer(v)

    @field_validator("question_id")
    @classmethod
    def validate_qid(cls, v: int) -> int:
        if not (0 <= v <= 999):
            raise ValueError("Invalid question_id.")
        return v

    @field_validator("streak")
    @classmethod
    def validate_streak(cls, v: int) -> int:
        return max(0, min(v, 500))


class SubmitResponse(BaseModel):
    correct:         bool
    score_delta:     int
    total_score:     int   # user's cumulative total across all modes
    message:         str
    leaderboard:     list  # top-10 global leaderboard (rank/username/total_score/total_correct)
    completed:       bool  # True when ALL questions in the mode are now answered correctly
    already_correct: bool  # True when this question was already answered correctly before


# Endpoints, fixed order (specific before parametric)

@router.post("/submit", response_model=SubmitResponse)
async def submit_answer(
    body:     SubmitRequest,
    request:  Request,
    response: Response,
    _csrf:    None = Depends(require_csrf),
    user:     User = Depends(get_current_user),
    db:       AsyncSession = Depends(get_db),
):
    """
    Server-side answer validation.  The correct answer is never in the browser.
    Scoring: 10 base + (streak-1)*2 bonus for each correct streak continuation.
    Integrity: verified against the signed kyber_session cookie set by /session.
    """
    # Verify game-session integrity cookie
    session_token = request.cookies.get("kyber_session")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active game session. Please log in again.",
        )
    uid_str = verify_session_cookie(session_token)
    if not uid_str or int(uid_str) != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired game session. Please log in again.",
        )

    challenge = get_challenge(body.mode, body.question_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Question not found.")

    correct = validate_answer(challenge, body.answer)

    # Was this question already answered correctly in a previous attempt?
    prev_res = await db.execute(
        select(Submission.id).where(
            Submission.user_id     == user.id,
            Submission.mode        == body.mode,
            Submission.question_id == body.question_id,
            Submission.correct     == True,
        ).limit(1)
    )
    already_correct = prev_res.scalar_one_or_none() is not None

    # Points are only awarded for questions not yet answered correctly.
    # Retrying a perfectly-completed level always yields 0 points per question.
    if already_correct:
        score_delta = 0
    else:
        score_delta = (10 + max(0, body.streak - 1) * 2) if correct else 0

    # Persist submission
    db.add(Submission(
        user_id=user.id,
        mode=body.mode,
        question_id=body.question_id,
        correct=correct,
        score_delta=score_delta,
    ))

    # Upsert leaderboard row
    res = await db.execute(
        select(Leaderboard).where(
            Leaderboard.user_id == user.id,
            Leaderboard.mode    == body.mode,
        )
    )
    entry = res.scalar_one_or_none()
    if entry is None:
        entry = Leaderboard(
            user_id=user.id, mode=body.mode,
            total_attempts=0, total_correct=0, best_score=0, best_streak=0,
        )
        db.add(entry)

    entry.total_attempts = (entry.total_attempts or 0) + 1
    # Only update correct-count / score / streak for newly-correct questions.
    if correct and not already_correct:
        entry.total_correct = (entry.total_correct or 0) + 1
        entry.best_score    = (entry.best_score    or 0) + score_delta
        entry.best_streak   = max(entry.best_streak or 0, body.streak + 1)

    # Level-completion check
    # Count distinct question_ids answered correctly (before this flush).
    # If the current answer is newly correct, add 1 manually because the new
    # Submission hasn't been flushed yet.
    total_q = len(ANSWER_KEYS[body.mode])
    dist_res = await db.execute(
        select(func.count(func.distinct(Submission.question_id))).where(
            Submission.user_id == user.id,
            Submission.mode    == body.mode,
            Submission.correct == True,
        )
    )
    distinct_correct = (dist_res.scalar() or 0) + (1 if (correct and not already_correct) else 0)
    level_completed  = (distinct_correct == total_q)

    if level_completed and entry.completed_at is None:
        entry.completed_at = datetime.now(timezone.utc)

    await db.flush()

    # Fetch updated global leaderboard (top 10)
    lb_result = await db.execute(
        select(
            User.username,
            func.sum(Leaderboard.best_score).label("total_score"),
            func.sum(Leaderboard.total_correct).label("total_correct"),
        )
        .join(Leaderboard, User.id == Leaderboard.user_id)
        .group_by(User.id, User.username)
        .order_by(desc("total_score"))
        .limit(10)
    )
    lb_rows = lb_result.all()
    leaderboard = [
        {
            "rank":          i + 1,
            "username":      r.username,
            "total_score":   r.total_score  or 0,
            "total_correct": r.total_correct or 0,
        }
        for i, r in enumerate(lb_rows)
    ]

    # User's own total across all modes
    user_total_res = await db.execute(
        select(func.sum(Leaderboard.best_score))
        .where(Leaderboard.user_id == user.id)
    )
    user_total = int(user_total_res.scalar() or 0)

    # Set score cookie (JS-readable, 30-day)
    response.set_cookie(
        key="kyber_score",
        value=str(user_total),
        httponly=False,
        samesite="lax",
        path="/",
        max_age=30 * 86400,
    )

    if already_correct and correct:
        message = "Already answered correctly, no points awarded."
    elif correct:
        message = "Correct! Level complete!" if level_completed else "Correct!"
    else:
        message = "Wrong, review the theory."

    return SubmitResponse(
        correct=correct,
        score_delta=score_delta,
        total_score=user_total,
        message=message,
        leaderboard=leaderboard,
        completed=level_completed,
        already_correct=already_correct,
    )


@router.get("/progress/{mode}")
async def get_progress(
    mode: str,
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    """Return the user's submission history for one mode (for resume support)."""
    if mode not in VALID_MODES:
        raise HTTPException(status_code=404, detail=f"Mode '{mode}' not found.")

    result = await db.execute(
        select(Submission)
        .where(Submission.user_id == user.id, Submission.mode == mode)
        .order_by(Submission.created_at)
    )
    rows = result.scalars().all()

    # Last attempt per question (most recent wins)
    answered: dict[int, bool] = {}
    for s in rows:
        answered[s.question_id] = s.correct

    # A question "counts" as correctly answered if ANY submission was correct.
    correctly_answered_ids = {s.question_id for s in rows if s.correct}
    total_q    = len(ANSWER_KEYS[mode])
    completed  = len(correctly_answered_ids) == total_q

    # Leaderboard row for completed_at (if any)
    lb_res = await db.execute(
        select(Leaderboard.completed_at).where(
            Leaderboard.user_id == user.id,
            Leaderboard.mode    == mode,
        )
    )
    lb_row = lb_res.scalar_one_or_none()
    completed_at = lb_row.isoformat() if lb_row else None

    return {
        "mode":          mode,
        "answered":      answered,
        "correct_count": len(correctly_answered_ids),
        "total_score":   sum(s.score_delta for s in rows),
        "completed":     completed,
        "completed_at":  completed_at,
    }


@router.get("/{mode}")
async def get_challenges(
    mode: str,
    user: User = Depends(get_current_user),
):
    """
    Return question metadata for a mode, type info only, NO correct answers.
    The frontend already holds all question text client-side.
    """
    if mode not in VALID_MODES:
        raise HTTPException(status_code=404, detail=f"Mode '{mode}' not found.")
    return get_mode_meta(mode)
