# main.py
import argparse, subprocess, sys, pathlib, os

def stream(cmd, cwd=None, env=None):
    proc = subprocess.Popen(
        cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in proc.stdout:
        print(line, end="")
    return proc.wait()

def run_in_container(repo_dir, image="codehealer-agent:latest"):
    repo_dir = pathlib.Path(repo_dir).resolve()
    if not repo_dir.is_dir():
        print(f"[host] ❌ {repo_dir} is not a directory")
        sys.exit(1)

    container_cmd = [
        "docker", "run", "--rm",
        "-e", f"OPENAI_API_KEY={os.environ.get('OPENAI_API_KEY','')}",
        "-v", f"{repo_dir}:/work",  # mount dir directly
        image,
        "python", "/app/run_in_container.py", "--workdir", "/work"
    ]
    return stream(container_cmd)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="Path to repo directory")
    args = ap.parse_args()
    run_in_container(args.dir)

if __name__ == "__main__":
    main()
