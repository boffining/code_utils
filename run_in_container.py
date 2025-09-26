# run_in_container.py
import argparse
import sys
import os
from codehealer.core.healer import Healer

def main():
    """
    Entry point for the code healing process inside the Docker container.
    This script orchestrates the healing process by using the Healer class,
    which embodies the agentic workflow for diagnosing and fixing code.
    """
    # Ensure OPENAI_API_KEY is available
    if not os.getenv("OPENAI_API_KEY"):
        print("[container] ❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("[container] Please set it before running the Docker container.")
        return 1
        
    parser = argparse.ArgumentParser(
        description="Run the CodeHealer agent inside a container to fix a Python repository."
    )
    parser.add_argument(
        "--workdir", 
        required=True, 
        help="The path to the repository to be healed (mounted inside the container)."
    )
    args = parser.parse_args()

    print("=============================================")
    print("    CodeHealer - Autonomous Repair Agent     ")
    print("=============================================")
    print(f"[container] Starting to heal repository at: {args.workdir}")

    try:
        # The Healer class encapsulates the agentic logic. It will:
        # 1. Set up a sandboxed virtual environment.
        # 2. Attempt to install dependencies, using an EnvironmentAgent to fix
        #    requirements.txt if installation fails.
        # 3. Attempt to run the code, using a CodeAgent to fix runtime errors
        #    like NameError, ImportError, etc., if they occur.
        # This approach is agentic as it follows a stateful, tool-using loop
        # similar to what would be designed with a framework like LangGraph.
        healer = Healer(repo_path=args.workdir)
        healer.heal()
        
        print("\n[container] ✅ Healing process completed successfully.")
        return 0
    except Exception as e:
        print(f"\n[container] ❌ An unexpected error occurred during the healing process: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
