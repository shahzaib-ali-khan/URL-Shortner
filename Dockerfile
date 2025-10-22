# ======================
# 1. Builder stage
# ======================
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq-dev gcc \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry self add poetry-plugin-export

COPY pyproject.toml poetry.lock /app/

# Export requirements and install dependencies
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && find /install -type f -name '*.pyc' -delete

# ======================
# 2. Runtime stage
# ======================
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]