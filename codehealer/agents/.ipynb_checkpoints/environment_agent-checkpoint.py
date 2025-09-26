from typing import Optional, List
from codehealer.agents.base_agent import BaseAgent

class EnvironmentAgent(BaseAgent):
    """An agent specializing in fixing and creating dependency files."""

    def __init__(self, repo_path: str):
        system_prompt = """
        You are an expert in Python dependency management. Your primary strategy is to simplify dependencies.

        Your task is to fix or create a `requirements.txt` file.

        **If fixing an existing file:** You will be given a `pip install` error log and the file content. Your default strategy should be to remove version specifiers (e.g., change `scipy==1.8.0` to `scipy`) to allow pip to resolve the latest stable version. Only add a specific version if the error log explicitly requires it.

        **If the `requirements.txt` file is missing:** You will be given all the Python source code from the repository. Your task is to generate a `requirements.txt` file from scratch by identifying all third-party libraries from the import statements. Do not include standard Python libraries.

        If you are shown previous failed attempts, it means those solutions did not work. You must provide a DIFFERENT and CORRECT solution.

        You MUST respond with ONLY the content for the new `requirements.txt` file. Do not include explanations, apologies, or markdown formatting.
        """
        super().__init__(repo_path, system_prompt)

    def get_suggestion(self, error_log: str, requirements_content: Optional[str] = None, attempt_history: Optional[List[str]] = None) -> str:
        """Analyzes a pip error or source code to suggest a requirements.txt file."""
        history_prompt = ""
        if attempt_history:
            history_prompt = "\n\nWe have tried to fix this before. Here are the previous `requirements.txt` contents that failed:\n"
            for i, attempt in enumerate(attempt_history):
                history_prompt += f"\n--- FAILED ATTEMPT {i+1} ---\n{attempt}\n--- END FAILED ATTEMPT {i+1} ---\n"
            history_prompt += "\nThe previous fixes did not resolve the error. Please analyze the situation again and provide a DIFFERENT and CORRECT fix."

        if requirements_content:
            # Mode 1: Fix existing requirements.txt
            user_prompt = f"""
            The command `pip install -r requirements.txt` failed with the following error:

            --- PIP ERROR LOG ---
            {error_log}
            --- END ERROR LOG ---

            Here is the content of the `requirements.txt` file:

            --- requirements.txt ---
            {requirements_content}
            --- END requirements.txt ---
            {history_prompt}
            Please provide the corrected content for the `requirements.txt` file.
            """
        else:
            # Mode 2: Generate requirements.txt from source code
            user_prompt = f"""
            The `requirements.txt` file is missing. Please generate it based on the repository's source code below. Identify all third-party imports.

            --- REPOSITORY SOURCE CODE ---
            {error_log}
            --- END REPOSITORY SOURCE CODE ---
            {history_prompt}
            Please provide the complete content for the new `requirements.txt` file.
            """

        return self._query_llm(user_prompt).strip()

