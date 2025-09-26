import os
import difflib
from pathlib import Path
from typing import Optional, Union


class FileHandler:
    """Handles reading from, writing to, and discovering files."""

    def __init__(self, base_path: Optional[Union[str, os.PathLike]] = None) -> None:
        """Create a handler optionally tied to a repository root.

        Historically the class was instantiated without any arguments.  Recent
        callers (such as :class:`codehealer.agents.code_agent.CodeAgent`) expect
        to be able to provide a repository path.  To remain backward compatible
        we accept an optional ``base_path`` while keeping the zero-argument
        constructor working for existing tests and code.
        """

        self.base_path = Path(base_path).resolve() if base_path is not None else None

    def _normalize_path(self, file_path: Union[str, os.PathLike]) -> Path:
        """Return a ``Path`` instance for ``file_path``."""

        return Path(file_path)

    def read_file(self, file_path: Union[str, os.PathLike]) -> Optional[str]:
        try:
            path = self._normalize_path(file_path)
            with path.open('r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path: Union[str, os.PathLike], content: str):
        """Writes content to a file and prints a colored diff of the changes."""
        path = self._normalize_path(file_path)
        original_content = self.read_file(path) or ""
        diff = "".join(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"a/{os.path.relpath(path)}",
            tofile=f"b/{os.path.relpath(path)}"
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
            with path.open('w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")

    def list_all_python_files(self, root_path: Optional[Union[str, os.PathLike]] = None) -> dict[str, str]:
        """Lists all python files in a directory.

        Parameters
        ----------
        root_path:
            Optional path to search.  When omitted we fall back to the
            ``base_path`` provided at construction time.
        """

        search_root: Optional[Path]
        if root_path is not None:
            search_root = Path(root_path)
        else:
            search_root = self.base_path

        if search_root is None:
            raise ValueError("No root path provided for listing python files.")

        search_root = search_root.resolve()
        py_files = {}
        for root, _, files in os.walk(search_root):
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    relative_path = os.path.relpath(full_path, search_root)
                    content = self.read_file(full_path)
                    if content:
                        py_files[relative_path] = content
        return py_files

