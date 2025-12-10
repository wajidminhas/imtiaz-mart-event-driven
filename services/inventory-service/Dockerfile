FROM python:3.11-slim

# Install uv package manager
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose inventory service port
EXPOSE 8004

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
