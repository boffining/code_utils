import re
import os
from typing import Optional, List, Tuple

from codehealer.agents.base_agent import BaseAgent
from codehealer.utils.file_handler import FileHandler

class CodeAgent(BaseAgent):
    """An agent that analyzes, fixes, and creates Python code holistically."""

    def __init__(self, repo_path: str):
        system_prompt = """
        You are an expert Python programmer acting as a senior developer performing a code review. Your task is to fix a Python project that has failed or is incomplete.

        You will be given the full traceback of an error (or a message indicating a missing file), and the complete source code for all Python files in the repository.

        Your goal is not just to fix a single error, but to **proactively identify and fix any other potential bugs** and to **create missing files** as needed. This includes:
        - **Creating an entry point:** If `main.py` or `app.py` is missing, analyze the project and create one that runs the primary functionality.
        - `NameError`: Correcting typos in variable or function names.
        - `ImportError` / `ModuleNotFoundError`: Adding or correcting import statements.
        - Obvious logical errors or typos.

        Analyze all the provided source code holistically. If you make a change in one file, consider if it affects others.

        If you are shown previous failed attempts, it means those solutions did not work. You must provide a DIFFERENT and more insightful solution.

        You MUST respond in the following format, providing complete, corrected content for every file you change or create.

        FILEPATH: path/to/the/first/file/to/fix.py
        ```python
        # The full, corrected content of the first python file goes here.
        ```
        ---
        FILEPATH: path/to/the/second/file/to/fix.py
        ```python
        # The full, corrected content of the second python file goes here.
        ```

        The filepaths must be relative to the repository root. Do not include any other text or explanations.
        """
        super().__init__(repo_path, system_prompt)
        self.file_handler = FileHandler(self.repo_path)

    def get_suggestion(self, traceback_log: str, attempt_history: Optional[List[str]] = None) -> Optional[List[Tuple[str, str]]]:
        """Analyzes a Python traceback or project state and suggests proactive code fixes."""
        history_prompt = ""
        if attempt_history:
            history_prompt = "\n\nWe have tried to fix this before. Here are the previous code changes that failed:\n"
            for i, attempt in enumerate(attempt_history):
                history_prompt += f"\n--- FAILED ATTEMPT {i+1} ---\n```python\n{attempt}\n```\n--- END FAILED ATTEMPT {i+1} ---\n"
            history_prompt += "\nThe previous fixes did not resolve the error. Please analyze the traceback and entire codebase again and provide a DIFFERENT and CORRECT fix."

        all_files = self.file_handler.list_all_python_files(self.repo_path)
        source_code_prompt = "\n--- REPOSITORY SOURCE CODE ---\n"
        for path, content in all_files.items():
            source_code_prompt += f"--- FILE: {path} ---\n"
            source_code_prompt += f"{content}\n"
        source_code_prompt += "--- END REPOSITORY SOURCE CODE ---\n"

        user_prompt = f"""
        The python project has an issue. The error traceback or status is:

        --- TRACEBACK / STATUS ---
        {traceback_log}
        --- END TRACEBACK / STATUS ---

        {source_code_prompt}
        {history_prompt}

        Please analyze the entire repository and the status. Provide complete, corrected content for any files that need to be fixed or created in the specified format.
        """
        response = self._query_llm(user_prompt)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> Optional[List[Tuple[str, str]]]:
        """Parses the LLM response to extract multiple filepaths and code blocks."""
        fixes = []
        # Split the response by the '---' separator for multiple files
        file_blocks = response.strip().split('\n---\n')

        for block in file_blocks:
            if not block.strip():
                continue
            try:
                filepath_match = re.search(r"FILEPATH: (.+)", block)
                code_match = re.search(r"```python\n(.*?)\n```", block, re.DOTALL)
                if filepath_match and code_match:
                    relative_filepath = filepath_match.group(1).strip().lstrip('/')
                    normalized_relative_path = os.path.normpath(relative_filepath)
                    abs_filepath = os.path.join(self.repo_path, normalized_relative_path)

                    if not os.path.abspath(abs_filepath).startswith(os.path.abspath(self.repo_path)):
                        print(f"Error: Agent suggested a path outside the repository: {relative_filepath}")
                        continue # Skip this block but process others

                    code = code_match.group(1).strip()
                    fixes.append((abs_filepath, code))
                else:
                    pass
            except Exception as e:
                print(f"Error parsing a block in the agent response: {e}")

        return fixes if fixes else None

