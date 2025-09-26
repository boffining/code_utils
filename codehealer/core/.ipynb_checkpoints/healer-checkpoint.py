import os
import time
from ..agents.env_agent import EnvironmentAgent
from ..agents.code_agent import CodeAgent
from ..utils.runner import Runner
from ..utils.file_handler import FileHandler
from ..utils.sandbox import SandboxManager

class Healer:
    """Orchestrates the healing process within a secure sandbox."""

    def __init__(self, repo_path: str, max_iterations: int = 10):
        self.repo_path = repo_path
        self.max_iterations = max_iterations
        self.iteration = 0

        # Core components. SandboxManager creates a venv *inside* the container.
        self.sandbox = SandboxManager(repo_path)
        self.runner = Runner(self.repo_path, self.sandbox)
        self.file_handler = FileHandler()
        self.env_agent = EnvironmentAgent(self.repo_path)
        self.code_agent = CodeAgent(self.repo_path)

    def heal(self):
        """Main healing loop. Sets up a sandbox and runs healing phases."""
        try:
            print("Setting up secure venv sandbox inside container...")
            self.sandbox.create()

            if not self._heal_environment():
                print("\n❌ Could not heal the environment. Aborting.")
                return

            print("\n✅ Environment is stable. Moving to runtime analysis.")

            if not self._heal_runtime():
                print("\n❌ Could not heal the runtime errors. Aborting.")
                return

            print("\n✨ Repository healed successfully! Code installs and runs without error.")

        finally:
            print("Cleaning up venv sandbox...")
            self.sandbox.cleanup()

    def _heal_environment(self) -> bool:
        """Ensures all dependencies are installed correctly inside the sandbox."""
        print("\n--- Phase 1: Resolving Environment ---")
        requirements_path = self.runner.find_requirements()
        if not requirements_path:
            print("No requirements.txt found. Assuming environment is okay.")
            return True

        for _ in range(self.max_iterations):
            self.iteration += 1
            print(f"\n[Attempt {self.iteration}] Installing dependencies in sandbox...")
            exit_code, log = self.runner.install_dependencies()

            if exit_code == 0:
                print("Dependencies installed successfully.")
                return True

            print("Dependency installation failed. Consulting EnvironmentAgent...")
            original_reqs = self.file_handler.read_file(requirements_path)
            suggestion = self.env_agent.get_suggestion(log, original_reqs)

            if not suggestion:
                print("Agent provided no suggestion. Retrying may not help.")
                return False

            print("Applying suggested fix to requirements.txt...")
            self.file_handler.write_file(requirements_path, suggestion)
            time.sleep(1)
        return False

    def _heal_runtime(self) -> bool:
        """Ensures the main application entry point runs without crashing."""
        print("\n--- Phase 2: Resolving Runtime Errors ---")
        entry_point = self.runner.find_entry_point()
        if not entry_point:
            print("Could not find a main entry point (main.py, app.py).")
            return True 
        
        print(f"Found entry point: {entry_point}")

        for _ in range(self.max_iterations - self.iteration):
            self.iteration += 1
            print(f"\n[Attempt {self.iteration}] Running application in sandbox...")
            exit_code, log = self.runner.run_entry_point(entry_point)

            if exit_code == 0:
                print("Application ran successfully without crashing.")
                return True

            print("Runtime error detected. Consulting CodeAgent...")
            fix = self.code_agent.get_suggestion(log)

            if not fix:
                print("Agent could not determine a fix.")
                return False
            
            file_to_patch, new_content = fix
            print(f"Applying suggested fix to {os.path.basename(file_to_patch)}...")
            self.file_handler.write_file(file_to_patch, new_content)
            time.sleep(1)
        return False

