"""
SQLAlchemy ORM models, maps to MySQL tables.
All tables use utf8mb4 charset and InnoDB engine.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey,
    Integer, SmallInteger, String, Text, UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


# Users
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email",    name="uq_users_email"),
        {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"},
    )

    id:            Mapped[int]           = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username:      Mapped[str]           = mapped_column(String(32),  nullable=False)
    email:         Mapped[str]           = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str]           = mapped_column(String(255), nullable=False)
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)
    is_admin:      Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)
    login_attempts: Mapped[int]          = mapped_column(SmallInteger, default=0, nullable=False)
    locked_until:  Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:    Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_login:    Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    submissions:   Mapped[list["Submission"]]    = relationship(back_populates="user", lazy="select")
    leaderboard:   Mapped[list["Leaderboard"]]   = relationship(back_populates="user", lazy="select")


# Submissions, every answered question
class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("ix_submissions_user_mode", "user_id", "mode"),
        Index("ix_submissions_created",   "created_at"),
        {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"},
    )

    id:          Mapped[int]      = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id:     Mapped[int]      = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mode:        Mapped[str]      = mapped_column(String(16), nullable=False)  # easy/medium/hard/...
    question_id: Mapped[int]      = mapped_column(Integer,   nullable=False)
    correct:     Mapped[bool]     = mapped_column(Boolean,   nullable=False)
    score_delta: Mapped[int]      = mapped_column(Integer,   default=0)
    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="submissions")


# Leaderboard, aggregated per-user per-mode
class Leaderboard(Base):
    __tablename__ = "leaderboard"
    __table_args__ = (
        UniqueConstraint("user_id", "mode", name="uq_leaderboard_user_mode"),
        Index("ix_leaderboard_mode_score", "mode", "best_score"),
        {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"},
    )

    id:           Mapped[int]      = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id:      Mapped[int]      = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mode:         Mapped[str]      = mapped_column(String(16), nullable=False)
    best_score:   Mapped[int]      = mapped_column(Integer, default=0)
    total_correct: Mapped[int]     = mapped_column(Integer, default=0)
    total_attempts: Mapped[int]    = mapped_column(Integer, default=0)
    best_streak:  Mapped[int]      = mapped_column(Integer, default=0)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at:   Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="leaderboard")


# Refresh token blacklist, invalidated tokens
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    __table_args__ = (
        Index("ix_revoked_tokens_jti", "jti"),
        {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"},
    )

    id:         Mapped[int]      = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    jti:        Mapped[str]      = mapped_column(String(64), nullable=False, unique=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
