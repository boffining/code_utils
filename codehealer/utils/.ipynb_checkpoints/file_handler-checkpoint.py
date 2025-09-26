import os

class FileHandler:
    """Handles reading from and writing to files."""
    def read_file(self, file_path: str) -> str | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path: str, content: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")
