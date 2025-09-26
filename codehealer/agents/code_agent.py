import re
import os
from .base_agent import BaseAgent
from ..utils.file_handler import FileHandler

class CodeAgent(BaseAgent):
    """An agent specializing in fixing Python runtime errors."""

    def __init__(self, repo_path: str):
        system_prompt = """
        You are an expert Python programmer. Your task is to fix a runtime error in a Python script.
        You will be given the full traceback of the error. Your job is to identify the faulty file, and provide its complete, corrected content.
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

    def get_suggestion(self, traceback_log: str) -> tuple[str, str] | None:
        """Analyzes a Python traceback and suggests a code fix."""
        user_prompt = f"""
        The python script failed with the following traceback:

        --- TRACEBACK ---
        {traceback_log}
        --- END TRACEBACK ---

        Please identify the file that needs to be fixed and provide its complete, corrected content in the specified format.
        """
        response = self._query_llm(user_prompt)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> tuple[str, str] | None:
        """Parses the LLM response to extract the filepath and code."""
        try:
            filepath_match = re.search(r"FILEPATH: (.+)", response)
            code_match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)

            if filepath_match and code_match:
                relative_filepath = filepath_match.group(1).strip().lstrip('/')
                abs_filepath = os.path.normpath(os.path.join(self.repo_path, relative_filepath))
                
                if not abs_filepath.startswith(self.repo_path):
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
