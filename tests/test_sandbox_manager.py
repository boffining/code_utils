import venv

from codehealer.utils.sandbox import SandboxManager


def test_create_invokes_venv_creation(monkeypatch, tmp_path):
    repo = tmp_path
    target = repo / ".codehealer_venv"
    created = {}

    def fake_cleanup(self):
        created["cleanup_called"] = True

    def fake_create(path, with_pip):
        created["venv_path"] = path
        created["with_pip"] = with_pip

    manager = SandboxManager(str(repo))
    target.mkdir()
    monkeypatch.setattr(SandboxManager, "cleanup", fake_cleanup, raising=False)
    monkeypatch.setattr(venv, "create", fake_create)

    manager.create()

    assert created["cleanup_called"]
    assert created["venv_path"] == str(target)
    assert created["with_pip"] is True


def test_get_python_and_pip_paths(tmp_path, monkeypatch):
    repo = tmp_path
    manager = SandboxManager(str(repo), venv_name="venv")
    base = repo / "venv"
    expected_python = base / "bin" / "python"
    expected_pip = base / "bin" / "pip"

    monkeypatch.setattr("sys.platform", "linux", raising=False)

    assert manager.get_python_executable() == str(expected_python)
    assert manager.get_pip_executable() == str(expected_pip)


def test_cleanup_removes_directory(tmp_path):
    repo = tmp_path
    manager = SandboxManager(str(repo), venv_name="venv")
    target = repo / "venv"
    target.mkdir()
    (target / "file.txt").write_text("data", encoding="utf-8")

    manager.cleanup()
    assert not target.exists()
