from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# Import the components that will be in the state, breaking the circular dependency
from codehealer.utils.sandbox import SandboxManager
from codehealer.utils.runner import Runner
from codehealer.utils.file_handler import FileHandler
from codehealer.agents.environment_agent import EnvironmentAgent
from codehealer.agents.code_agent import CodeAgent

class AgentState(TypedDict):
    """Defines the state of the agent at any point in the graph."""
    # The tools and components are now first-class citizens of the state
    sandbox: SandboxManager
    runner: Runner
    file_handler: FileHandler
    env_agent: EnvironmentAgent
    code_agent: CodeAgent

    # Metadata for the run
    iteration: int
    max_iterations: int
    log: str
    is_success: bool
    phase: str

def setup_sandbox_node(state: AgentState) -> dict:
    """Node: Creates the sandboxed virtual environment."""
    sandbox = state["sandbox"]
    print("\n--- Phase 1: Setting up Sandbox ---")
    sandbox.create()
    print("✅ Sandbox created.")
    # Return only the keys that are being updated
    return {
        "iteration": 0,
        "phase": "environment"
    }

def heal_environment_node(state: AgentState) -> dict:
    """Node: Attempts to install dependencies, healing them if necessary."""
    runner = state["runner"]
    file_handler = state["file_handler"]
    env_agent = state["env_agent"]
    
    iteration = state['iteration'] + 1
    update = {"iteration": iteration}
    print(f"\n--- Phase 2: Resolving Environment (Attempt {iteration}) ---")
    
    requirements_path = runner.find_requirements()
    if not requirements_path:
        print("No requirements.txt found. Skipping to runtime analysis.")
        update.update({"is_success": True, "phase": "runtime"})
        return update

    exit_code, log = runner.install_dependencies()
    update["log"] = log

    if exit_code == 0:
        print("✅ Dependencies installed successfully.")
        update.update({"is_success": True, "phase": "runtime"})
    else:
        print("Dependency installation failed. Consulting EnvironmentAgent...")
        original_reqs = file_handler.read_file(requirements_path)
        suggestion = env_agent.get_suggestion(log, original_reqs)
        
        if suggestion:
            print("Applying suggested fix to requirements.txt...")
            file_handler.write_file(requirements_path, suggestion)
            update["is_success"] = False # Stay in this phase to retry
        else:
            print("❌ Agent provided no suggestion. Cannot heal environment.")
            update.update({"is_success": False, "phase": "fail"})
            
    return update

def heal_runtime_node(state: AgentState) -> dict:
    """Node: Attempts to run the code, healing runtime errors if they occur."""
    runner = state["runner"]
    code_agent = state["code_agent"]
    file_handler = state["file_handler"]
    
    iteration = state['iteration'] + 1
    update = {"iteration": iteration}
    print(f"\n--- Phase 3: Resolving Runtime Errors (Attempt {iteration}) ---")

    entry_point = runner.find_entry_point()
    if not entry_point:
        print("Could not find a main entry point. Checking for importable packages.")
        update["is_success"] = True
        return update

    exit_code, log = runner.run_entry_point(entry_point)
    update["log"] = log

    if exit_code == 0:
        print(f"✅ Entry point '{entry_point}' ran successfully.")
        update["is_success"] = True
    else:
        print("Runtime error detected. Consulting CodeAgent...")
        fix = code_agent.get_suggestion(log)

        if fix:
            file_to_patch, new_content = fix
            print(f"Applying suggested fix to {file_to_patch}...")
            file_handler.write_file(file_to_patch, new_content)
            update["is_success"] = False # Stay in this phase to retry
        else:
            print("❌ Agent could not determine a fix for the runtime error.")
            update.update({"is_success": False, "phase": "fail"})
            
    return update

def decide_next_step(state: AgentState) -> str:
    """Edge: Decides the next node to visit based on the current state."""
    if state["phase"] == "fail":
        return "fail"
        
    if state["iteration"] >= state["max_iterations"]:
        print("\n❌ Reached maximum iterations. Aborting.")
        return "fail"

    if state["phase"] == "environment":
        return "heal_environment"
    
    if state["phase"] == "runtime":
        if state["is_success"]:
            # If runtime healing was successful, we're done.
            return "finish"
        else:
            # If it failed but a fix was applied, retry.
            return "heal_runtime"
    
    # This should not be reached
    return "fail"

def build_graph():
    """Builds the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("setup_sandbox", setup_sandbox_node)
    workflow.add_node("heal_environment", heal_environment_node)
    workflow.add_node("heal_runtime", heal_runtime_node)
    workflow.add_node("finish", lambda state: print("\n✨ Repository healed successfully!"))
    workflow.add_node("fail", lambda state: print("\n❌ Healing process failed."))

    # Define edges
    workflow.set_entry_point("setup_sandbox")
    workflow.add_edge("setup_sandbox", "heal_environment")
    
    workflow.add_conditional_edges(
        "heal_environment",
        lambda state: "heal_runtime" if state["is_success"] else decide_next_step(state),
        {"heal_runtime": "heal_runtime", "heal_environment": "heal_environment", "fail": "fail"}
    )
    
    workflow.add_conditional_edges(
        "heal_runtime",
        decide_next_step,
        {"finish": "finish", "heal_runtime": "heal_runtime", "fail": "fail"}
    )
    
    workflow.add_edge("finish", END)
    workflow.add_edge("fail", END)

    return workflow.compile()

