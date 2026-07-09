# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure uv to use the system Python (no project .venv)
ENV UV_SYSTEM_PYTHON=1
ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies only
RUN uv sync --frozen --no-cache --no-install-project

# Copy application source
COPY . .

# Install the project
RUN uv sync --frozen --no-cache

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]