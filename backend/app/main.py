"""
CRYSTALS-Kyber Training Platform, FastAPI Application

Startup sequence:
  1. DB engine created (connection pool, not yet connected)
  2. Redis client created (not yet connected)
  3. Lifespan runs: creates DB tables, pings Redis
  4. Health endpoint immediately returns 200 once uvicorn is up
     (Docker healthcheck only checks /health, not DB/Redis)

Middleware stack (outermost → innermost):
  TrustedHost → CORS → SecurityHeaders → RateLimit → GZip
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config           import settings
from app.core.database         import Base, engine
from app.core.redis_client     import get_redis
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security   import SecurityHeadersMiddleware
from app.routers               import auth, challenges, leaderboard, users

log = structlog.get_logger()


# Lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup.begin", env=settings.APP_ENV)

    # Create DB tables (idempotent, safe to run every boot)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("startup.db", status="ok")
    except Exception as exc:
        log.error("startup.db", status="failed", error=str(exc))
        raise  # abort startup, container will be unhealthy, Docker will restart

    # Verify Redis
    try:
        redis = await get_redis()
        await redis.ping()
        log.info("startup.redis", status="ok")
    except Exception as exc:
        log.error("startup.redis", status="failed", error=str(exc))
        raise

    log.info("startup.complete")
    yield

    await engine.dispose()
    log.info("shutdown.complete")


# App

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url    ="/api/docs"         if settings.APP_ENV == "development" else None,
    redoc_url   ="/api/redoc"        if settings.APP_ENV == "development" else None,
    openapi_url ="/api/openapi.json" if settings.APP_ENV == "development" else None,
)


# Middleware (add_middleware inserts outermost each time)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],   # tighten to your domain in production
)


# Exception handlers

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """Clean 422, never leak internal field names or stack traces."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data."},
    )


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    """Catch-all, log server-side, return safe generic message."""
    log.error("unhandled_exception", path=request.url.path, exc=repr(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
    )


# Routers

app.include_router(auth.router,        prefix="/api/auth",        tags=["auth"])
app.include_router(users.router,       prefix="/api/users",       tags=["users"])
app.include_router(challenges.router,  prefix="/api/challenges",  tags=["challenges"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])


# Health

@app.get("/health", include_in_schema=False)
async def health():
    """
    Docker HEALTHCHECK endpoint.
    Returns 200 as soon as uvicorn is serving, before DB/Redis are verified.
    The lifespan will crash the process if DB or Redis are unreachable,
    which Docker will catch via the health check timing out.
    """
    return {"status": "ok"}
