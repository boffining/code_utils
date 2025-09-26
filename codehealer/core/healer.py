import os
from codehealer.agents.environment_agent import EnvironmentAgent
from codehealer.agents.code_agent import CodeAgent
from codehealer.utils.runner import Runner
from codehealer.utils.file_handler import FileHandler
from codehealer.utils.sandbox import SandboxManager
from codehealer.core.graph import build_graph, AgentState

class Healer:
    """Orchestrates the healing process using a LangGraph-defined workflow."""

    def __init__(self, repo_path: str, max_iterations: int = 10):
        self.repo_path = repo_path
        self.max_iterations = max_iterations
        
        # Core components remain the same
        self.sandbox = SandboxManager(repo_path)
        self.runner = Runner(self.repo_path, self.sandbox)
        self.file_handler = FileHandler()
        self.env_agent = EnvironmentAgent(self.repo_path)
        self.code_agent = CodeAgent(self.repo_path)
        
        # Compile the agentic workflow from the graph definition
        self.app = build_graph()

    def heal(self):
        """
        Executes the healing process by invoking the compiled LangGraph agent.
        The graph handles setup, environment healing, runtime healing, and manages
        the iterative loop until success or failure.
        """
        initial_state: AgentState = {
            "healer": self,
            "iteration": 0,
            "max_iterations": self.max_iterations,
            "log": "",
            "is_success": False,
            "phase": "setup"
        }
        
        try:
            # Run the graph from the initial state
            self.app.invoke(initial_state)
        finally:
            print("\nCleaning up venv sandbox...")
            self.sandbox.cleanup()
