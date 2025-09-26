# Use a slim, official Python image as the base
FROM python:3.11-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy the entire CodeHealer project into the container's WORKDIR
# This includes the codehealer package, pyproject.toml, etc.
COPY . .

# Install the CodeHealer tool and its dependencies (e.g., openai)
# The '.' tells pip to install from the current directory based on pyproject.toml
RUN pip install .

# Set the entry point for the container. When the container runs, it will
# execute this script. The command-line arguments from `docker run` will be
# passed to this script.
ENTRYPOINT ["python", "run_in_container.py"]

