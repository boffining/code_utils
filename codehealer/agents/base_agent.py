import os
from openai import OpenAI

class BaseAgent:
    """Abstract base class for all agents."""

    def __init__(self, repo_path: str, system_prompt: str):
        self.repo_path = repo_path
        self.system_prompt = system_prompt
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=api_key)

    def _query_llm(self, user_prompt: str) -> str:
        """Sends a query to the LLM and returns the response."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error communicating with OpenAI API: {e}")
            return ""
