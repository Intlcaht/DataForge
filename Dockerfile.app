# Stage 1: Builder
FROM python:alpine AS builder

# Set workdir
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Install pip tools
COPY ./app/src/pyproject.toml poetry.lock ./
RUN pip install poetry && poetry export -f requirements.txt --without-hashes > requirements.txt

# Install app dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy source code
COPY ./app/src/. .
COPY ./app/main.py .

# Stage 2: Runtime
FROM python:alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Expose API port
EXPOSE 8000

# Set entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
