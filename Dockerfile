# Dockerfile (snippet)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir pytest

# Copy codehealer runtime
COPY run_in_container.py /app/run_in_container.py
