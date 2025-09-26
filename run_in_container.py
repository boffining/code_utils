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

def parse_nameerror(trace):
    lines = trace.splitlines()
    file_path, missing = None, None
    for i, line in enumerate(lines):
        if "NameError:" in line:
            if "'" in line:
                missing = line.split("'")[1]
            for j in range(i-1, -1, -1):
                if lines[j].strip().startswith('File "'):
                    file_path = lines[j].split('"')[1]
                    break
            break
    return file_path, missing

def add_missing_import(file_path, missing):
    code = pathlib.Path(file_path).read_text()
    new_code = f"import {missing}\n{code}"
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

    repo_dir = pathlib.Path(args.workdir)
    print(f"[container] Healing repo at {repo_dir}")

    for attempt in range(1, 6):
        print(f"[container] === Attempt {attempt} ===")
        rc, out = run_cmd(["python", "main.py"], cwd=repo_dir)
        if rc == 0:
            print("[container] ✅ Success!")
            return 0

        if "NameError" in out:
            file_path, missing = parse_nameerror(out)
            print(f"[container] Fixing NameError: {missing} in {file_path}")
            add_missing_import(file_path, missing)
            continue

        if "ImportError" in out:
            print("[container] Detected ImportError. (Add pip install logic here)")
            # Optionally run pip install inside container
            continue

        print("[container] Could not fix automatically.")
        return 1
    return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
