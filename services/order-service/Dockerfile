
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create venv and install dependencies IN the container
RUN uv venv && uv sync

# Copy application code
COPY . .

# Use the container's venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8003

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]