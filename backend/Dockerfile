#  Backend Dockerfile — FastAPI / Python 3.11
#  Multi-stage: builder compiles C extensions, runtime has no build tools.
#  Runs as non-root appuser (UID 1001).

# Stage 1: build wheels
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# Stage 2: runtime
FROM python:3.11-slim AS runtime

# Runtime deps: libmariadb3 provides libmysqlclient.so for mysqlclient wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
        libmariadb3 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r appgroup -g 1001 \
 && useradd  -r -u 1001 -g appgroup -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install wheels built in stage 1
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
 && rm -rf /wheels

# Copy application source
COPY app/ ./app/

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# Health check
# start_period=60s gives DB + app time to fully initialise before Docker
# starts counting failures. interval=15s so we detect problems quickly after.
HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=4 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--no-access-log", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
