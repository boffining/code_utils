import subprocess
from types import SimpleNamespace

import pytest

from codehealer.utils.runner import Runner
from codehealer.utils.sandbox import SandboxManager


class DummySandbox(SandboxManager):
    def __init__(self, repo_path):
        super().__init__(repo_path)
        self.python_path = "python"
        self.pip_path = "pip"

    def get_python_executable(self):
        return self.python_path

    def get_pip_executable(self):
        return self.pip_path


def test_run_command_success(monkeypatch, temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    runner = Runner(str(temp_repo), sandbox)

    def fake_run(command, cwd, capture_output, text, timeout):
        assert command == ["python", "--version"]
        return SimpleNamespace(returncode=0, stdout="Python", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    code, output = runner._run_command(["python", "--version"])
    assert code == 0
    assert "Python" in output


def test_run_command_handles_exception(monkeypatch, temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    runner = Runner(str(temp_repo), sandbox)

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="python", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    code, output = runner._run_command(["python"])
    assert code == -1
    assert "Failed to execute" in output


def test_find_requirements(temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    runner = Runner(str(temp_repo), sandbox)
    assert runner.find_requirements() is None

    req = temp_repo / "requirements.txt"
    req.write_text("flask", encoding="utf-8")
    assert runner.find_requirements() == str(req)


def test_install_dependencies_invokes_pip(monkeypatch, temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    sandbox.pip_path = "pip3"
    runner = Runner(str(temp_repo), sandbox)

    req = temp_repo / "requirements.txt"
    req.write_text("flask", encoding="utf-8")

    called = {}

    def fake_run_command(command):
        called["command"] = command
        return 0, "ok"

    monkeypatch.setattr(runner, "_run_command", fake_run_command)
    code, output = runner.install_dependencies()
    assert code == 0
    assert called["command"] == ["pip3", "install", "-r", str(req)]
    assert output == "ok"


def test_install_dependencies_when_missing_requirements(temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    runner = Runner(str(temp_repo), sandbox)
    code, output = runner.install_dependencies()
    assert code == 0
    assert "No requirements" in output


def test_find_entry_point(temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    runner = Runner(str(temp_repo), sandbox)
    assert runner.find_entry_point() is None

    entry = temp_repo / "main.py"
    entry.write_text("print('hi')", encoding="utf-8")
    assert runner.find_entry_point() == "main.py"


def test_run_entry_point(temp_repo, monkeypatch):
    sandbox = DummySandbox(str(temp_repo))
    sandbox.python_path = "python3"
    runner = Runner(str(temp_repo), sandbox)

    called = {}

    def fake_run_command(command):
        called["command"] = command
        return 0, "ran"

    monkeypatch.setattr(runner, "_run_command", fake_run_command)
    code, output = runner.run_entry_point("main.py")
    assert code == 0
    assert called["command"] == ["python3", "main.py"]
    assert output == "ran"


def test_discover_importable_packages(temp_repo):
    (temp_repo / "pkg").mkdir()
    (temp_repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (temp_repo / "not_a_package").mkdir()

    sandbox = DummySandbox(str(temp_repo))
    runner = Runner(str(temp_repo), sandbox)

    assert runner.discover_importable_packages() == ["pkg"]


def test_import_package_invokes_python(monkeypatch, temp_repo):
    sandbox = DummySandbox(str(temp_repo))
    sandbox.python_path = "python3"
    runner = Runner(str(temp_repo), sandbox)

    called = {}

    def fake_run_command(command):
        called["command"] = command
        return 0, "ok"

    monkeypatch.setattr(runner, "_run_command", fake_run_command)
    code, output = runner.import_package("pkg")

    assert code == 0
    assert output == "ok"
    assert called["command"] == ["python3", "-c", "import pkg"]
