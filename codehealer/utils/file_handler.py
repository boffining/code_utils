import os
import difflib
from typing import Optional

class FileHandler:
    """Handles reading from, writing to, and discovering files."""

    def read_file(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path: str, content: str):
        """Writes content to a file and prints a colored diff of the changes."""
        original_content = self.read_file(file_path) or ""
        diff = "".join(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"a/{os.path.relpath(file_path)}",
            tofile=f"b/{os.path.relpath(file_path)}"
        ))
        
        # Color the diff for better readability
        colored_diff = []
        for line in diff.splitlines():
            if line.startswith('+'):
                colored_diff.append(f"\033[92m{line}\033[0m") # Green
            elif line.startswith('-'):
                colored_diff.append(f"\033[91m{line}\033[0m") # Red
            elif line.startswith('^'):
                continue
            else:
                colored_diff.append(line)
        
        print("[container] --- BEGIN DIFF ---")
        print("\n".join(colored_diff))
        print("[container] --- END DIFF ---")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")

    def list_all_python_files(self, root_path: str) -> dict[str, str]:
        """Lists all python files in a directory and returns a dict of relative_path: content."""
        py_files = {}
        for root, _, files in os.walk(root_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, root_path)
                    content = self.read_file(full_path)
                    if content:
                        py_files[relative_path] = content
        return py_files

