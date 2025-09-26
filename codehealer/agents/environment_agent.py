from codehealer.agents.base_agent import BaseAgent

class EnvironmentAgent(BaseAgent):
    """An agent specializing in fixing dependency installation errors."""

    def __init__(self, repo_path: str):
        system_prompt = """
        You are an expert in Python dependency management. Your task is to fix a `requirements.txt` file that is causing a `pip install` error.
        You will be given the error log from pip and the content of the `requirements.txt` file.
        Your goal is to provide a corrected version of the ENTIRE `requirements.txt` file.
        You MUST respond with ONLY the content for the new `requirements.txt` file. Do not include explanations, apologies, or markdown formatting.
        For example, if a version doesn't exist, find a valid one. If there's a typo, fix it.
        """
        super().__init__(repo_path, system_prompt)

    def get_suggestion(self, error_log: str, requirements_content: str) -> str:
        """Analyzes a pip error and suggests a fix for requirements.txt."""
        user_prompt = f"""
        The command `pip install -r requirements.txt` failed with the following error:

        --- PIP ERROR LOG ---
        {error_log}
        --- END ERROR LOG ---

        Here is the content of the `requirements.txt` file:

        --- requirements.txt ---
        {requirements_content}
        --- END requirements.txt ---

        Please provide the corrected content for the `requirements.txt` file.
        """
        return self._query_llm(user_prompt).strip()