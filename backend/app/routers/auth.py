"""
Auth router — /api/auth/*

Routes:
  POST /api/auth/register   — create new account
  POST /api/auth/login      — returns JWT access token + HttpOnly refresh cookie
  POST /api/auth/logout     — revoke refresh token, clear cookies
  POST /api/auth/refresh    — issue new access token from refresh cookie
  GET  /api/auth/csrf-token — get a CSRF token for state-changing requests

Security implemented:
  - bcrypt password hashing (rounds from BCRYPT_ROUNDS env)
  - Constant-time comparison (prevents timing attacks on missing users)
  - Redis-backed brute-force lockout (MAX_LOGIN_ATTEMPTS per LOCKOUT_MINUTES)
  - Refresh token stored HttpOnly, SameSite=strict — not readable by JS
  - CSRF token returned as readable cookie — JS must echo it in X-CSRF-Token header
  - JTI-based refresh token revocation stored in MySQL
"""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config       import settings
from app.core.database     import get_db
from app.core.deps         import get_current_user
from app.core.redis_client import get_redis
from app.core.security     import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_csrf_token,
    hash_password,
    sanitise_username,
    sign_session_cookie,
    verify_password,
)
from app.models.models import RevokedToken, User

router = APIRouter()


# Schemas

class RegisterRequest(BaseModel):
    username: str
    email:    EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        return sanitise_username(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if len(v) > 128:
            raise ValueError("Password too long.")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# Redis key helpers

def _attempt_key(username: str) -> str:
    return f"login_attempts:{username}"

def _lockout_key(username: str) -> str:
    return f"login_locked:{username}"


# Brute-force helpers

async def _check_lockout(username: str, redis) -> None:
    if await redis.exists(_lockout_key(username)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {settings.LOCKOUT_MINUTES} minutes.",
        )


async def _record_failure(username: str, redis) -> None:
    key     = _attempt_key(username)
    count   = await redis.incr(key)
    ttl     = settings.LOCKOUT_MINUTES * 60
    await redis.expire(key, ttl)
    if count >= settings.MAX_LOGIN_ATTEMPTS:
        await redis.setex(_lockout_key(username), ttl, "1")


async def _clear_failures(username: str, redis) -> None:
    await redis.delete(_attempt_key(username), _lockout_key(username))


# Endpoints

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db:   AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(User).where(
            (User.username == body.username) | (User.email == str(body.email))
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered.",
        )

    db.add(User(
        username=body.username,
        email=str(body.email),
        password_hash=hash_password(body.password),
    ))
    await db.flush()
    return {"message": "Account created. You can now log in."}


@router.post("/login", response_model=TokenResponse)
async def login(
    body:     LoginRequest,
    response: Response,
    db:       AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    await _check_lockout(body.username, redis)

    result = await db.execute(select(User).where(User.username == body.username))
    user: User | None = result.scalar_one_or_none()

    # Constant-time path — run bcrypt even when user doesn't exist
    # This prevents timing-based user enumeration.
    _DUMMY = "$2b$12$zZ3c0OoRLOn/lDNzqBB17OxXdQQ.C9t4.bq5zEfFEaE7o8DzqOspu"
    stored = user.password_hash if user else _DUMMY

    if not verify_password(body.password, stored) or user is None:
        await _record_failure(body.username, redis)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )

    await _clear_failures(body.username, redis)
    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    access_token  = create_access_token(
        str(user.id),
        extra={"role": "admin" if user.is_admin else "user"},
    )
    refresh_token = create_refresh_token(str(user.id))

    # Refresh token: HttpOnly, not readable by JS, SameSite=strict
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.TLS_ENABLED,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth/refresh",
    )

    # CSRF token: readable by JS (httponly=False), JS sends it as X-CSRF-Token
    response.set_cookie(
        key="csrf_token",
        value=generate_csrf_token(str(user.id)),
        httponly=False,
        secure=settings.TLS_ENABLED,
        samesite="strict",
        max_age=settings.CSRF_TOKEN_EXPIRE,
        path="/",
    )

    # Game-session integrity cookie: HttpOnly, signed uid, 7-day lifetime
    response.set_cookie(
        key="kyber_session",
        value=sign_session_cookie(str(user.id)),
        httponly=True,
        secure=settings.TLS_ENABLED,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )

    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response:      Response,
    refresh_token: str | None = Cookie(default=None),
    db:            AsyncSession = Depends(get_db),
):
    if refresh_token:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            jti = payload.get("jti")
            if jti:
                exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
                db.add(RevokedToken(jti=jti, expires_at=exp))
                await db.flush()
        except Exception:
            pass  # invalid/expired token — still clear cookie

    response.delete_cookie("refresh_token",  path="/api/auth/refresh")
    response.delete_cookie("csrf_token",     path="/")
    response.delete_cookie("kyber_session",  path="/")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: str | None = Cookie(default=None),
    db:            AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided.",
        )
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    # Check revocation list
    jti = payload.get("jti", "")
    row = await db.execute(select(RevokedToken).where(RevokedToken.jti == jti))
    if row.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked.",
        )

    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user   = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/csrf-token")
async def get_csrf_token(user: User = Depends(get_current_user)):
    """
    Issue a CSRF token tied to the authenticated user's ID.
    The JS layer must read this and send it as X-CSRF-Token on every mutation.
    Verification in require_csrf also uses str(user.id) — they must match.
    """
    return {"csrf_token": generate_csrf_token(str(user.id))}
