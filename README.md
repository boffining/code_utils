# CodeHealer 3.0 🩺⚙️

**CodeHealer** is an autonomous Python repair assistant that runs entirely inside an isolated
Docker container. Supply a zipped Python project, and it builds a sandboxed environment,
repairs the code, and hands back a fixed archive—no manual debugging required.

---

## 🚀 Highlights
- **Container-first safety** – All healing happens inside the `codehealer-agent` Docker image.
- **Bring-your-own project** – Feed in any zipped Python repository and get a patched version back.
- **Minimal host setup** – You only need Python 3.10+, Docker, and an OpenAI API key.
- **Zip-in / Zip-out workflow** – Perfect for CI pipelines and reproducible fixes.

---

## 🧱 Architecture at a Glance
| Layer | What happens there? |
| --- | --- |
| **Host Orchestrator** (`main.py`) | Unzips your project, builds the Docker image, runs the container, then re-zips the healed code. |
| **Container Runtime** (`run_in_container.py`) | Creates an internal virtual environment, analyzes the repo, applies fixes, and validates the run. |
| **Agents & Utilities** (`codehealer/`) | The brains of the operation—specialized agents that coordinate analysis, dependency repair, and execution. |

---

## 🛠️ Quickstart (6 steps)
1. **Install prerequisites**
   - Python 3.10 or newer
   - Docker Engine running locally
   - An `OPENAI_API_KEY`

2. **Set up an isolated environment (optional but recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install CodeHealer in editable mode**
   ```bash
   pip install -e .
   ```

4. **Zip a sample project**
   We include `examples/hello_codehealer/` for smoke-testing. Create an archive with the
   Python stdlib so no extra tools are required:
   ```bash
   python -m zipfile -c examples/hello_codehealer_target.zip examples/hello_codehealer
   ```

5. **Point CodeHealer at the zipped project**
   ```bash
   export OPENAI_API_KEY="sk-your-key"
   python main.py --zip-path examples/hello_codehealer_target.zip
   ```
   The first run builds the Docker image; subsequent runs reuse it.

6. **Validate the fixed project**
   The healed archive is saved as `examples/hello_codehealer_target_fixed.zip` in the current
   directory. Unzip it and run the target script to confirm success:
   ```bash
   unzip examples/hello_codehealer_target_fixed.zip -d healed_repo
   python healed_repo/app.py
   ```
   Expected output:
   ```
   Hello from the CodeHealer target repo!
   ```

---

## 🧪 Demo Target Repository
We include `examples/hello_codehealer/`, a minimal project used in the Quickstart walkthrough.
Its README documents the expected output so you can quickly verify that the healed archive
matches the intended behavior.

---

## 📂 Repository Layout
```
.
├── codehealer/              # Core agents, orchestration logic, and utilities
├── examples/
│   └── hello_codehealer/    # Sample target repo used in the quickstart
├── main.py                  # Host-side orchestration (unzips, runs Docker, re-zips)
├── run_in_container.py      # Container entrypoint for the healing workflow
├── Dockerfile               # Defines the codehealer-agent runtime image
└── pyproject.toml           # Python package metadata (only depends on `openai`)
```

---

## ❓ Troubleshooting
- **`docker: command not found`** – Install Docker and ensure the daemon is running.
- **`OPENAI_API_KEY` missing** – Export your key before running `main.py`.
- **Permission errors on macOS/Linux** – Prefix Docker commands with `sudo` if your user is
  not part of the `docker` group.

Happy healing! 🛠️
