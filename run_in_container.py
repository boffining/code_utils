import argparse
import os
from codehealer.core.healer import Healer

def main():
    """
    This script is the entry point for the Docker container.
    It's a lightweight wrapper that kicks off the healing process
    on the code repository mounted into the container.
    """
    parser = argparse.ArgumentParser(
        description="Run the CodeHealer process inside a container."
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="The path to the mounted code repository inside the container (e.g., /workspace/repo)."
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="The maximum number of attempts to fix the code."
    )
    args = parser.parse_args()

    # Check if the API key is available in the container's environment
    if not os.getenv("OPENAI_API_KEY"):
        print("FATAL: OPENAI_API_KEY environment variable not found inside the container.")
        return

    # Instantiate and run the main Healer orchestrator
    healer = Healer(repo_path=args.path, max_iterations=args.max_iterations)
    healer.heal()


if __name__ == "__main__":
    main()

