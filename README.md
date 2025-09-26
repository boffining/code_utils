CodeHealer 3.0: Containerized Autonomous Python Healer 📦✨
CodeHealer is an autonomous AI agent that makes any Python repository runnable. This version operates within a secure Docker container, providing maximum isolation and safety. It takes a zipped repository as input, heals it, and returns a new zipped file with the fixes.

Key Features
Containerized Sandboxing: All operations—dependency installation and code execution—happen inside a Docker container. This provides full filesystem and process isolation, ensuring the tool cannot affect your host machine.

Zero Host Dependencies (Almost!): The tool only requires Python and a running Docker daemon on your host machine. All project-specific dependencies are handled inside the container.

Zip-In, Zip-Out Workflow: Designed for portability and ease-of-use. You provide a .zip file of the buggy code and get back a _fixed.zip file.

Fully Autonomous: Automatically discovers dependencies, entry points, and fixes both environment and runtime errors without any user configuration.

Lightweight & Extensible: The core agent-based architecture is preserved, making it easy to add new capabilities.

Architecture: The Host and The Container
The new architecture creates a clean separation of concerns between a Host Orchestrator and a Containerized Healer.

1. Host Orchestrator (main.py)

This script runs on your machine. It does not perform any healing itself. Its only job is to manage the Docker lifecycle.

Workflow:

Takes a --zip-path argument (e.g., buggy_project.zip).

Creates a temporary directory.

Unzips the repository into the temporary directory.

Builds the codehealer-agent Docker image from the Dockerfile.

Runs a new container from that image, mounting the unzipped code directory into the container's /workspace/repo.

Passes your OPENAI_API_KEY securely into the container as an environment variable.

Waits for the container to finish the healing process.

Zips the now-modified code from the temporary directory into a new file (e.g., buggy_project_fixed.zip).

Cleans up the temporary directory and the container.

2. Containerized Healer (run_in_container.py & Core Logic)

This is the core healing engine that lives and runs exclusively inside the Docker container.

Environment: The Dockerfile defines a clean environment with Python and the CodeHealer tool's dependencies pre-installed.

Workflow:

The ENTRYPOINT of the container starts the run_in_container.py script.

This script receives the path to the mounted code (/workspace/repo).

It instantiates the Healer orchestrator, which proceeds with the two-phase healing process (Environment & Runtime) exactly as before, but now fully isolated from your system.

The SandboxManager still creates a venv, but it does so inside the container. This provides a second layer of isolation for the project's dependencies from the tool's own dependencies within the container.

Usage
Prepare your buggy project:
Ensure your buggy Python project is in a zip file (e.g., buggy_project.zip). For this demo, you can create one from the example_repo_4 directory:

# (On macOS/Linux)
zip -r buggy_project.zip example_repo_4/

# (On Windows, using PowerShell)
Compress-Archive -Path example_repo_4\* -DestinationPath buggy_project.zip

Install the package (for the host orchestrator script):

pip install -e .

Set your API key:

export OPENAI_API_KEY='your-api-key'

Run the Healer:
Point the tool at your zipped repository. It will build the Docker image on the first run and then execute the healing process.

python main.py --zip-path ./buggy_project.zip

Upon completion, you will find a buggy_project_fixed.zip file in your directory.

