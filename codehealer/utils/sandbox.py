import os
import sys
import venv
import shutil

class SandboxManager:
    """Manages the creation, use, and cleanup of a dedicated virtual environment."""

    def __init__(self, repo_path: str, venv_name: str = ".codehealer_venv"):
        self.repo_path = repo_path
        self.venv_path = os.path.join(self.repo_path, venv_name)

    def create(self):
        """Creates a new virtual environment."""
        if os.path.exists(self.venv_path):
            self.cleanup()
        print(f"Creating virtual environment at: {self.venv_path}")
        try:
            venv.create(self.venv_path, with_pip=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create virtual environment: {e}")

    def get_python_executable(self) -> str:
        """Returns the path to the python executable within the venv."""
        if sys.platform == "win32":
            return os.path.join(self.venv_path, "Scripts", "python.exe")
        else:
            return os.path.join(self.venv_path, "bin", "python")

    def get_pip_executable(self) -> str:
        """Returns the path to the pip executable within the venv."""
        if sys.platform == "win32":
            return os.path.join(self.venv_path, "Scripts", "pip.exe")
        else:
            return os.path.join(self.venv_path, "bin", "pip")

    def cleanup(self):
        """Removes the virtual environment directory."""
        if os.path.exists(self.venv_path):
            print(f"Removing virtual environment: {self.venv_path}")
            try:
                shutil.rmtree(self.venv_path)
            except OSError as e:
                print(f"Warning: Could not remove sandbox directory {self.venv_path}: {e}")
