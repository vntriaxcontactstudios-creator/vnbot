# VNBOT API — Dockerfile for Fase 0.2
# Build: docker build -t vnbot-api -f services/api/Dockerfile .
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY packages/ ./packages/
COPY services/api/ ./services/api/

# Install dependencies
RUN uv sync --all-packages --no-dev

# Expose port
EXPOSE 8000

# Run
CMD ["uv", "run", "uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
