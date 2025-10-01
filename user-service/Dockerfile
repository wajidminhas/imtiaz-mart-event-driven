# Use a slim Python base image
FROM python:3.11-slim

# Install uv (fastest Python installer)
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock (if you have one)
COPY pyproject.toml .
# COPY uv.lock .   # ← optional, for reproducible builds

COPY uv.lock .
# Install only runtime dependencies (uv sync without --dev)
RUN uv sync --frozen --no-dev

# Copy application source code
COPY . .

# Expose the app port
EXPOSE 8001

# Run the service
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]