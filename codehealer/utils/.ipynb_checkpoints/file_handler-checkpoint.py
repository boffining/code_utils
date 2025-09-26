from typing import Optional
import difflib
import os

class FileHandler:
    """Handles reading from and writing to files."""

    def read_file(self, file_path: str) -> Optional[str]:
        """Reads the entire content of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path: str, content: str):
        """Writes content to a file and prints a colored diff of the changes."""
        original_content = ""
        if os.path.exists(file_path):
            original_content = self.read_file(file_path) or ""

        # Do not write or print a diff if the content is identical.
        if original_content == content:
            return

        print(f"\n[file_handler] Applying changes to {os.path.basename(file_path)}:")
        
        diff = difflib.unified_diff(
            original_content.splitlines(),
            content.splitlines(),
            fromfile=f"a/{os.path.basename(file_path)}",
            tofile=f"b/{os.path.basename(file_path)}",
            lineterm="",
        )
        
        diff_lines = list(diff)
        if not diff_lines:
            print("[file_handler] Content changed but no textual diff to display (e.g., whitespace).")
        else:
            for line in diff_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    # Green for additions
                    print(f'\033[92m{line}\033[0m')
                elif line.startswith('-') and not line.startswith('---'):
                    # Red for deletions
                    print(f'\033[91m{line}\033[0m')
                elif line.startswith('@@'):
                    # Cyan for context line
                    print(f'\033[96m{line}\033[0m')
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[file_handler] Wrote changes to {file_path}\n")
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")
