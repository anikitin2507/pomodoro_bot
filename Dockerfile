FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy app code
COPY app/ ./app/
COPY pyproject.toml ./

# Install dependencies 
RUN pip install --no-cache-dir -e .

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Add entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER appuser

# Run the application
CMD ["/entrypoint.sh"] 