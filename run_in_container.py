# run_in_container.py
import argparse, subprocess, pathlib, difflib, os

def run_cmd(cmd, cwd):
    print(f"[container] $ {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output = []
    for line in proc.stdout:
        print(line, end="")
        output.append(line)
    return proc.wait(), "".join(output)

def parse_error(trace):
    lines = trace.splitlines()
    file_path, missing = None, None
    for i, line in enumerate(lines):
        if "NameError:" in line or "ModuleNotFoundError:" in line or "ImportError:" in line:
            if "'" in line:
                missing = line.split("'")[1]
            for j in range(i-1, -1, -1):
                if lines[j].strip().startswith('File "'):
                    file_path = lines[j].split('"')[1]
                    break
            break
    return file_path, missing

def apply_fix(file_path, new_code):
    code = pathlib.Path(file_path).read_text()
    diff = "".join(difflib.unified_diff(
        code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile=f"a/{file_path}", tofile=f"b/{file_path}"
    ))
    print("[container] --- BEGIN DIFF ---")
    print(diff)
    print("[container] --- END DIFF ---")
    pathlib.Path(file_path).write_text(new_code)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    args = ap.parse_args()

    # This is a placeholder for where the CodeAgent would be instantiated
    # In the full implementation, you would import and create an instance of CodeAgent
    # For this example, we'll simulate the agent's output.
    from codehealer.agents.code_agent import CodeAgent
    code_agent = CodeAgent(args.workdir)


    repo_dir = pathlib.Path(args.workdir)
    print(f"[container] Healing repo at {repo_dir}")

    for attempt in range(1, 6):
        print(f"[container] === Attempt {attempt} ===")
        rc, out = run_cmd(["python", "main.py"], cwd=repo_dir)
        if rc == 0:
            print("[container] ✅ Success!")
            return 0

        if "NameError" in out or "ModuleNotFoundError" in out or "ImportError" in out:
            print(f"[container] Detected error. Consulting CodeAgent...")
            fix = code_agent.get_suggestion(out)
            if fix:
                file_to_patch, new_content = fix
                print(f"Applying suggested fix to {os.path.basename(file_to_patch)}...")
                apply_fix(file_to_patch, new_content)
                continue

        print("[container] Could not fix automatically.")
        return 1
    return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())