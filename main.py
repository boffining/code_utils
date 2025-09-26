import argparse
import os
import subprocess
import tempfile
import shutil
import zipfile

def run_command(command, error_message):
    """Helper function to run a subprocess command and handle errors."""
    try:
        print(f"Executing: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {error_message}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    except FileNotFoundError:
        print("ERROR: 'docker' command not found. Is Docker installed and running?")
        raise


def main():
    """
    Main entry point on the HOST machine.
    Orchestrates the zip/unzip and Docker build/run process.
    """
    parser = argparse.ArgumentParser(
        description="Orchestrate the containerized healing of a zipped Python repository."
    )
    parser.add_argument(
        "--zip-path",
        type=str,
        required=True,
        help="Path to the .zip file of the repository to heal."
    )
    args = parser.parse_args()

    if not os.path.exists(args.zip_path):
        print(f"Error: The file '{args.zip_path}' does not exist.")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it before running: export OPENAI_API_KEY='your-key'")
        return

    # Create a temporary directory to work in
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = os.path.join(temp_dir, "repo")
        os.makedirs(repo_path)

        # 1. Unzip the user's repository
        print(f"Unzipping '{args.zip_path}' to temporary directory...")
        with zipfile.ZipFile(args.zip_path, 'r') as zip_ref:
            zip_ref.extractall(repo_path)

        # 2. Build the Docker image
        image_tag = "codehealer-agent:latest"
        build_command = ["docker", "build", "-t", image_tag, "."]
        run_command(build_command, "Failed to build Docker image.")

        # 3. Run the container, mounting the unzipped code
        # The '--rm' flag automatically removes the container when it exits.
        absolute_repo_path = os.path.abspath(repo_path)
        run_command = [
            "docker", "run", "--rm",
            "-v", f"{absolute_repo_path}:/workspace/repo",
            "-e", f"OPENAI_API_KEY={api_key}",
            image_tag,
            "--path", "/workspace/repo"
        ]
        run_command(run_command, "The healing process inside the container failed.")

        # 4. Zip up the fixed repository
        base_name, _ = os.path.splitext(os.path.basename(args.zip_path))
        output_zip_path_base = f"{base_name}_fixed"
        shutil.make_archive(output_zip_path_base, 'zip', repo_path)
        
        print("\n" + "="*60)
        print("✅ Healing complete!")
        print(f"Fixed repository saved to: {output_zip_path_base}.zip")
        print("="*60)

if __name__ == "__main__":
    main()

