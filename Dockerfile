# Dockerfile (snippet)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY codehealer/ /app/codehealer/
COPY run_in_container.py /app/run_in_container.py

# Install the codehealer package in editable mode.
# This makes it importable by other scripts in the container.
COPY pyproject.toml /app/
RUN pip install -e .
RUN pip install --no-cache-dir pytest langgraph

# Copy codehealer runtime
COPY run_in_container.py /app/run_in_container.py
