from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
import os

from codehealer.utils.sandbox import SandboxManager
from codehealer.utils.runner import Runner
from codehealer.utils.file_handler import FileHandler
from codehealer.agents.environment_agent import EnvironmentAgent
from codehealer.agents.code_agent import CodeAgent

class AgentState(TypedDict):
    sandbox: SandboxManager
    runner: Runner
    file_handler: FileHandler
    env_agent: EnvironmentAgent
    code_agent: CodeAgent
    iteration: int
    max_iterations: int
    log: str
    is_success: bool
    phase: str
    attempt_history: List[str]

def setup_sandbox_node(state: AgentState) -> dict:
    sandbox = state["sandbox"]
    print("\n--- Phase 1: Setting up Sandbox ---")
    sandbox.create()
    print("✅ Sandbox created.")
    return {"iteration": 0, "phase": "environment", "attempt_history": []}

def heal_environment_node(state: AgentState) -> dict:
    runner = state["runner"]
    file_handler = state["file_handler"]
    env_agent = state["env_agent"]
    
    iteration = state['iteration'] + 1
    attempt_history = state['attempt_history']
    update = {"iteration": iteration, "attempt_history": attempt_history}
    print(f"\n--- Phase 2: Resolving Environment (Attempt {iteration}) ---")
    
    requirements_path = runner.find_requirements()
    if not requirements_path:
        print("`requirements.txt` not found. Asking EnvironmentAgent to generate one...")
        all_files = file_handler.list_all_python_files(runner.repo_path)
        source_code_str = "\n".join(f"--- FILE: {path} ---\n{content}" for path, content in all_files.items())
        
        suggestion = env_agent.get_suggestion(source_code_str, None, attempt_history)
        
        if suggestion:
            new_req_path = os.path.join(runner.repo_path, 'requirements.txt')
            print(f"Applying suggested fix to create {os.path.basename(new_req_path)}...")
            file_handler.write_file(new_req_path, suggestion)
            attempt_history.append(suggestion)
            update["is_success"] = False # Loop back to try installing the new file
        else:
            print("❌ Agent provided no suggestion. Cannot create environment.")
            update.update({"is_success": False, "phase": "fail"})
        return update

    exit_code, log = runner.install_dependencies()
    update["log"] = log

    if exit_code == 0:
        print("✅ Dependencies installed successfully.")
        update.update({"is_success": True, "phase": "runtime", "attempt_history": []})
    else:
        print("Dependency installation failed. Consulting EnvironmentAgent...")
        original_reqs = file_handler.read_file(requirements_path)
        suggestion = env_agent.get_suggestion(log, original_reqs, attempt_history)
        
        if suggestion:
            print("Applying suggested fix to requirements.txt...")
            file_handler.write_file(requirements_path, suggestion)
            attempt_history.append(suggestion)
            update["is_success"] = False
        else:
            print("❌ Agent provided no suggestion. Cannot heal environment.")
            update.update({"is_success": False, "phase": "fail"})
            
    return update

def heal_runtime_node(state: AgentState) -> dict:
    runner = state["runner"]
    code_agent = state["code_agent"]
    file_handler = state["file_handler"]
    
    iteration = state['iteration'] + 1
    attempt_history = state['attempt_history']
    update = {"iteration": iteration, "attempt_history": attempt_history}
    print(f"\n--- Phase 3: Resolving Runtime Errors (Attempt {iteration}) ---")

    entry_point = runner.find_entry_point()
    if not entry_point:
        print("Entry point not found. Asking CodeAgent to generate one...")
        status_log = "No entry point found (e.g., main.py, app.py). Please analyze the repository and create one."
        fixes = code_agent.get_suggestion(status_log, attempt_history)
        if fixes:
            all_new_content = []
            for file_to_patch, new_content in fixes:
                print(f"Applying suggested change to create/update {os.path.basename(file_to_patch)}...")
                file_handler.write_file(file_to_patch, new_content)
                all_new_content.append(new_content)
            attempt_history.append("\n---\n".join(all_new_content))
            update["is_success"] = False # Loop back to try running the new entry point
        else:
            print("Could not generate an entry point. Checking for importable packages.")
            update["is_success"] = True # Move on to package import checks
        return update

    exit_code, log = runner.run_entry_point(entry_point)
    update["log"] = log

    if exit_code == 0:
        print(f"✅ Entry point '{entry_point}' ran successfully.")
        update["is_success"] = True
    else:
        print("Runtime error detected. Consulting CodeAgent...")
        fixes = code_agent.get_suggestion(log, attempt_history)
        if fixes:
            all_new_content = []
            for file_to_patch, new_content in fixes:
                print(f"Applying suggested fix to {os.path.basename(file_to_patch)}...")
                file_handler.write_file(file_to_patch, new_content)
                all_new_content.append(new_content)
            attempt_history.append("\n---\n".join(all_new_content))
            update["is_success"] = False
        else:
            print("❌ Agent could not determine a fix for the runtime error.")
            update.update({"is_success": False, "phase": "fail"})
            
    return update

def decide_next_step(state: AgentState) -> str:
    if state["phase"] == "fail":
        return "fail"
    if state["iteration"] >= state["max_iterations"]:
        print("\n❌ Reached maximum iterations. Aborting.")
        return "fail"
    if state["phase"] == "environment":
        return "heal_environment"
    if state["phase"] == "runtime":
        return "heal_runtime" if not state["is_success"] else "finish"
    return "fail"

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("setup_sandbox", setup_sandbox_node)
    workflow.add_node("heal_environment", heal_environment_node)
    workflow.add_node("heal_runtime", heal_runtime_node)
    workflow.add_node("finish", lambda state: print("\n✨ Repository healed successfully!"))
    workflow.add_node("fail", lambda state: print("\n❌ Healing process failed."))

    workflow.set_entry_point("setup_sandbox")
    workflow.add_edge("setup_sandbox", "heal_environment")
    
    workflow.add_conditional_edges(
        "heal_environment",
        lambda s: "heal_runtime" if s["is_success"] else decide_next_step(s),
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

