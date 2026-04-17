# Build Stage
FROM python:3.11-slim as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime Stage
FROM python:3.11-slim as runtime

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser
WORKDIR /app

# Ensure proper permissions and path
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy installed dependencies and adjust ownership
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy code and adjust ownership
COPY --chown=appuser:appuser app/ app/
COPY --chown=appuser:appuser utils/ utils/

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check (pointing to the internal port)
HEALTHCHECK --interval=30s --timeout=15s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Using python -m uvicorn ensures it uses the installed package in the path
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
