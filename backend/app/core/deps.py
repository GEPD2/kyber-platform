"""
Shared FastAPI dependencies injected via Depends().
  - get_current_user  — verifies JWT, returns User ORM object
  - require_csrf      — validates X-CSRF-Token header
  - get_current_admin — same as get_current_user but checks is_admin
"""

from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database  import get_db
from app.core.security  import decode_token, verify_csrf_token
from app.models.models  import User


# JWT bearer extraction

def _extract_bearer(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.removeprefix("Bearer ").strip()


async def get_current_user(
    token: str = Depends(_extract_bearer),
    db:    AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token, expected_type="access")
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise credentials_error
    except JWTError:
        raise credentials_error

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user   = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_error
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


# CSRF verification

async def require_csrf(
    request: Request,
    user:    User = Depends(get_current_user),
    x_csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> None:
    """
    Dependency that enforces CSRF token validation on state-changing requests.
    Inject with:  _ = Depends(require_csrf)
    The frontend must read the csrf_token cookie and send it as X-CSRF-Token header.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    if not x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing CSRF token.",
        )
    if not verify_csrf_token(x_csrf_token, str(user.id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token.",
        )
