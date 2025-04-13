# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-cache --only main

COPY . .

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Install netcat in the final stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy virtualenv and app code
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
COPY --from=builder /app/entrypoint.sh .

ENV PATH="/app/.venv/bin:$PATH"

RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
