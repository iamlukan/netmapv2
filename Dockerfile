# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml .

# Install dependencies into a temporary directory
# We can use pip directly to install from pyproject.toml as long as it adheres to standards or we export it
# Since we don't have uv in the image by default, let's just install standard pip tools
RUN pip install --upgrade pip && \
    pip install .

# Final stage
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run commands
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
