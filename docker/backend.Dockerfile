# EyeCare Backend Dockerfile
# Production-ready multi-stage build

# ==================== BUILD STAGE ====================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# ==================== PRODUCTION STAGE ====================
FROM python:3.11-slim AS production

LABEL maintainer="EyeCare Team" version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN groupadd -r eyecare && useradd -r -g eyecare eyecare

WORKDIR $APP_HOME

COPY --from=builder /opt/venv /opt/venv

COPY --chown=eyecare:eyecare backend/app ./app
COPY --chown=eyecare:eyecare backend/alembic ./alembic
COPY --chown=eyecare:eyecare backend/alembic.ini ./alembic.ini
COPY --chown=eyecare:eyecare docker/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh \
    && mkdir -p uploads/avatars uploads/reports logs \
    && chown -R eyecare:eyecare $APP_HOME

USER eyecare

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -sf http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
