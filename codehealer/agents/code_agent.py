import re
import os
from typing import Optional, Tuple, List

from .base_agent import BaseAgent
from ..utils.file_handler import FileHandler

class CodeAgent(BaseAgent):
    """An agent specializing in fixing Python runtime errors."""

    def __init__(self, repo_path: str):
        system_prompt = """
        You are an expert Python programmer. Your task is to fix a runtime error in a Python script.
        You will be given the source code of the file where the error occurred, and the full traceback.
        Your job is to provide the complete, corrected content of the file. Pay close attention to typos in function or variable names (e.g., `gree` instead of `greet`).
        If you are shown previous failed attempts, it means those solutions did not work. You must provide a DIFFERENT and CORRECT solution.
        You MUST respond in the following format:
        
        FILEPATH: path/to/the/file/to/fix.py
        ```python
        # The full, corrected content of the python file goes here.
        # Make sure to include the entire file, not just the changed part.
        ```
        
        The filepath must be relative to the repository root. Do not include any other text, explanations, or apologies.
        """
        super().__init__(repo_path, system_prompt)
        self.file_handler = FileHandler()

    def _extract_file_context_from_traceback(self, traceback_log: str) -> Optional[Tuple[str, str]]:
        """Parses a traceback to find the relevant source file and its content."""
        filepath_matches = re.findall(r'File "([^"]+)"', traceback_log)
        for path in reversed(filepath_matches):
            abs_path = os.path.abspath(path)
            repo_abs_path = os.path.abspath(self.repo_path)
            if abs_path.startswith(repo_abs_path):
                content = self.file_handler.read_file(abs_path)
                if content:
                    relative_path = os.path.relpath(abs_path, repo_abs_path)
                    return relative_path, content
        return None

    def get_suggestion(self, traceback_log: str, attempt_history: Optional[List[str]] = None) -> Optional[Tuple[str, str]]:
        """Analyzes a Python traceback and suggests a code fix."""
        context = self._extract_file_context_from_traceback(traceback_log)
        if not context:
            print("Could not find a relevant file in the traceback within the repository.")
            return None
        
        relative_path, file_content = context
        history_prompt = ""
        if attempt_history:
            history_prompt = "\n\nWe have tried to fix this before. Here are the previous attempts that failed:\n"
            for i, attempt in enumerate(attempt_history):
                history_prompt += f"\n--- FAILED ATTEMPT {i+1} ---\n```python\n{attempt}\n```\n--- END FAILED ATTEMPT {i+1} ---\n"
            history_prompt += "\nThe previous fixes did not resolve the error. Please analyze the traceback again and provide a DIFFERENT and CORRECT fix."

        user_prompt = f"""
        The python script failed.

        --- SOURCE CODE OF {relative_path} ---
        {file_content}
        --- END SOURCE CODE ---

        Here is the traceback:

        --- TRACEBACK ---
        {traceback_log}
        --- END TRACEBACK ---
        {history_prompt}
        Please analyze the source code and the traceback to identify the error. Provide the complete, corrected content for the file `{relative_path}` in the specified format.
        """
        response = self._query_llm(user_prompt)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> Optional[Tuple[str, str]]:
        """Parses the LLM response to extract the filepath and code."""
        try:
            filepath_match = re.search(r"FILEPATH: (.+)", response)
            code_match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
            if filepath_match and code_match:
                relative_filepath = filepath_match.group(1).strip().lstrip('/')
                normalized_relative_path = os.path.normpath(relative_filepath)
                abs_filepath = os.path.join(self.repo_path, normalized_relative_path)
                if not os.path.abspath(abs_filepath).startswith(os.path.abspath(self.repo_path)):
                    print(f"Error: Agent suggested a path outside the repository: {relative_filepath}")
                    return None
                code = code_match.group(1).strip()
                return abs_filepath, code
            else:
                print("Agent response was not in the expected format.")
                return None
        except Exception as e:
            print(f"Error parsing agent response: {e}")
            return None

