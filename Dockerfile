FROM python:3.13-slim

WORKDIR /app

# Install necessary system packages (minimal like backend)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock README.md ./

# Install UV package manager (same as backend)
RUN pip install --no-cache-dir uv

# Install dependencies using UV (same as backend)
RUN uv pip install --system -e .

# Copy application code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8001

# Run the application
CMD ["uv", "run", "firebase-auth"]
