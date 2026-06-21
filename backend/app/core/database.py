"""
Async SQLAlchemy engine + session factory.
All DB access goes through get_db() dependency.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    # pool_pre_ping is intentionally OFF: SQLAlchemy 2.0.30's aiomysql adapter
    # declares `ping(self, reconnect)` with no default, but its pre-ping path
    # calls `ping()` with no args (it inspects pymysql's `ping(self, reconnect=False)`
    # signature), raising "ping() missing 1 required positional argument: 'reconnect'"
    # on every reused connection. pool_recycle below keeps connections fresh instead.
    pool_pre_ping=False,
    pool_recycle=1800,        # recycle every 30 min (well under MySQL wait_timeout)
    echo=settings.DEBUG,      # SQL logging only in dev
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency: yields a DB session, always closes on exit."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
