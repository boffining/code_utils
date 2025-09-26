import subprocess
import os
from typing import List
from .sandbox import SandboxManager

class Runner:
    """Handles running external commands within a specified sandbox."""

    def __init__(self, repo_path: str, sandbox: SandboxManager):
        self.repo_path = repo_path
        self.sandbox = sandbox

    def _run_command(self, command: List[str]) -> tuple[int, str]:
        """A generic method to run a command and capture its output."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=180
            )
            return result.returncode, f"{result.stdout}\n{result.stderr}"
        except Exception as e:
            return -1, f"Failed to execute command '{' '.join(command)}': {e}"

    def find_requirements(self) -> str | None:
        path = os.path.join(self.repo_path, 'requirements.txt')
        return path if os.path.exists(path) else None

    def install_dependencies(self) -> tuple[int, str]:
        requirements_path = self.find_requirements()
        if not requirements_path:
            return 0, "No requirements.txt found."
        
        pip_exe = self.sandbox.get_pip_executable()
        return self._run_command([pip_exe, "install", "-r", requirements_path])

    def find_entry_point(self) -> str | None:
        common_files = ['main.py', 'app.py', 'run.py']
        for filename in common_files:
            path = os.path.join(self.repo_path, filename)
            if os.path.exists(path):
                return filename
        return None

    def run_entry_point(self, entry_point_filename: str) -> tuple[int, str]:
        python_exe = self.sandbox.get_python_executable()
        return self._run_command([python_exe, entry_point_filename])
