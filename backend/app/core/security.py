"""
Security utilities:
  - bcrypt password hashing / verification
  - JWT access + refresh token creation / verification
  - CSRF token generation and verification (itsdangerous HMAC)
  - Input sanitisation (XSS, path traversal, XXE, null bytes)

NOTE: pwd_context and _csrf_serializer are intentionally lazy-initialised
so that module import never triggers bcrypt benchmark or secret access.
"""

import html
import re
import secrets
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JWTError, jwt
from passlib.context import CryptContext


# Lazy singletons — built on first use, not at import time

@lru_cache(maxsize=1)
def _pwd_context() -> CryptContext:
    from app.core.config import settings
    return CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=settings.BCRYPT_ROUNDS,
    )

@lru_cache(maxsize=1)
def _csrf_serializer() -> URLSafeTimedSerializer:
    from app.core.config import settings
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt="csrf")

@lru_cache(maxsize=1)
def _session_serializer() -> URLSafeTimedSerializer:
    from app.core.config import settings
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt="kyber-game-session")


# Password hashing

def hash_password(plain: str) -> str:
    """Hash a password with bcrypt."""
    return _pwd_context().hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time bcrypt comparison. Returns False on any error."""
    try:
        return _pwd_context().verify(plain, hashed)
    except Exception:
        return False


# JWT tokens

def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    from app.core.config import settings
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub":  subject,
        "iat":  now,
        "exp":  now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    from app.core.config import settings
    now = datetime.now(timezone.utc)
    payload = {
        "sub":  subject,
        "iat":  now,
        "exp":  now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti":  secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> dict:
    from app.core.config import settings
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != expected_type:
            raise JWTError("wrong token type")
        return payload
    except JWTError:
        raise


# CSRF tokens

def generate_csrf_token(session_id: str) -> str:
    from app.core.config import settings
    return _csrf_serializer().dumps(session_id)


def verify_csrf_token(token: str, session_id: str) -> bool:
    from app.core.config import settings
    try:
        value = _csrf_serializer().loads(token, max_age=settings.CSRF_TOKEN_EXPIRE)
        return value == session_id
    except (BadSignature, SignatureExpired):
        return False


# Game-session cookie

_SESSION_MAX_AGE = 7 * 86400  # 7 days — matches REFRESH_TOKEN_EXPIRE_DAYS


def sign_session_cookie(user_id: str) -> str:
    """Return a signed token encoding the user id."""
    return _session_serializer().dumps({"uid": user_id})


def verify_session_cookie(token: str) -> str | None:
    """
    Verify the session cookie and return the uid string, or None on failure.
    Uses a 7-day max-age matching the refresh token lifetime.
    """
    try:
        data = _session_serializer().loads(token, max_age=_SESSION_MAX_AGE)
        return str(data.get("uid", ""))
    except (BadSignature, SignatureExpired):
        return None


# Input sanitisation

_PATH_TRAVERSAL = re.compile(r"\.\.[/\\]|[/\\]\.\.")
_NULL_BYTE       = re.compile(r"\x00")
_XXE_PATTERNS    = re.compile(r"<!ENTITY|SYSTEM\s+[\"']|<!DOCTYPE", re.IGNORECASE)


def sanitise_string(value: str, max_length: int = 512) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected string input")
    value = _NULL_BYTE.sub("", value)
    value = value[:max_length]
    value = html.escape(value, quote=True)
    return value


def sanitise_username(value: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9_\-]{3,32}", value):
        raise ValueError("Username must be 3-32 characters: letters, digits, _ or -")
    return value


def check_path_traversal(value: str) -> None:
    if _PATH_TRAVERSAL.search(value):
        raise ValueError("Path traversal detected in input")


def check_xxe(value: str) -> None:
    if _XXE_PATTERNS.search(value):
        raise ValueError("Disallowed XML content detected")


def sanitise_answer(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Answer must be a string")
    value = _NULL_BYTE.sub("", value)
    value = value.strip()[:256]
    check_path_traversal(value)
    check_xxe(value)
    return value
