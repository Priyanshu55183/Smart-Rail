# =============================================
# SmartRail Backend — Dockerfile
# =============================================
# Multi-stage build for a lean production image.
#
# Stage 1 (builder): Install all Python dependencies
# Stage 2 (runtime): Copy only what's needed to run
#
# Why multi-stage?
# - Dependencies change rarely → cached layer (fast rebuilds)
# - App code changes often → only this layer rebuilds
# - Final image is smaller (no build tools)

FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker cache optimization)
# If requirements.txt hasn't changed, this layer is cached
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Runtime Stage ─────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install runtime-only system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Health check — Docker uses this to know if the container is healthy
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run the FastAPI server
# --host 0.0.0.0: Listen on all interfaces (required inside Docker)
# --port 8000: The port we expose
# --reload: Auto-restart on code changes (dev only)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
