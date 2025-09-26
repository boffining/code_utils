import pytest

from codehealer.core.healer import Healer


class StubSandbox:
    def __init__(self):
        self.created = False
        self.cleaned = False

    def create(self):
        self.created = True

    def cleanup(self):
        self.cleaned = True


class StubRunner:
    def __init__(self):
        self.requirements = None
        self.install_attempts = []
        self.run_attempts = []
        self.entry_point = None
        self.install_index = 0
        self.run_index = 0

    def find_requirements(self):
        return self.requirements

    def install_dependencies(self):
        result = self.install_attempts[self.install_index]
        self.install_index += 1
        return result

    def find_entry_point(self):
        return self.entry_point

    def run_entry_point(self, entry_point):
        result = self.run_attempts[self.run_index]
        self.run_index += 1
        return result

    def reset(self):
        self.install_index = 0
        self.run_index = 0


class StubFileHandler:
    def __init__(self):
        self.read_calls = []
        self.write_calls = []
        self.content = {}

    def read_file(self, path):
        self.read_calls.append(path)
        return self.content.get(path, "")

    def write_file(self, path, content):
        self.write_calls.append((path, content))
        self.content[path] = content


class StubEnvAgent:
    def __init__(self):
        self.suggestions = []

    def get_suggestion(self, log, original):
        return self.suggestions.pop(0) if self.suggestions else None


class StubCodeAgent:
    def __init__(self):
        self.suggestions = []

    def get_suggestion(self, log):
        return self.suggestions.pop(0) if self.suggestions else None


@pytest.fixture
def healer(tmp_path, monkeypatch):
    instance = Healer(str(tmp_path), max_iterations=4)
    stub_runner = StubRunner()
    instance.sandbox = StubSandbox()
    instance.runner = stub_runner
    instance.file_handler = StubFileHandler()
    instance.env_agent = StubEnvAgent()
    instance.code_agent = StubCodeAgent()
    monkeypatch.setattr("time.sleep", lambda *_: None)
    return instance


def test_heal_success_path(healer):
    healer.runner.requirements = None
    healer.runner.entry_point = None

    healer.heal()

    assert healer.sandbox.created is True
    assert healer.sandbox.cleaned is True


def test_heal_environment_with_requirements_success(healer, tmp_path):
    req_path = str(tmp_path / "requirements.txt")
    healer.runner.requirements = req_path
    healer.file_handler.content[req_path] = "flask==0.1"
    healer.runner.install_attempts = [
        (1, "error"),
        (0, "ok"),
    ]
    healer.runner.reset()
    healer.env_agent.suggestions = ["flask==2.3.2"]

    assert healer._heal_environment() is True
    assert healer.file_handler.write_calls == [(req_path, "flask==2.3.2")]


def test_heal_environment_fails_without_suggestion(healer, tmp_path):
    req_path = str(tmp_path / "requirements.txt")
    healer.runner.requirements = req_path
    healer.file_handler.content[req_path] = "flask==0.1"
    healer.runner.install_attempts = [
        (1, "error"),
    ]
    healer.runner.reset()
    healer.env_agent.suggestions = []

    assert healer._heal_environment() is False


def test_heal_runtime_success(healer, tmp_path):
    file_to_patch = str(tmp_path / "app.py")
    healer.runner.entry_point = "main.py"
    healer.runner.run_attempts = [
        (1, "traceback"),
        (0, "ok"),
    ]
    healer.runner.reset()
    healer.code_agent.suggestions = [(file_to_patch, "print('fixed')")]

    assert healer._heal_runtime() is True
    assert healer.file_handler.write_calls[-1] == (file_to_patch, "print('fixed')")


def test_heal_runtime_no_entry_point(healer):
    healer.runner.entry_point = None
    assert healer._heal_runtime() is True


def test_heal_runtime_failure_without_fix(healer):
    healer.runner.entry_point = "main.py"
    healer.runner.run_attempts = [(1, "traceback")]
    healer.runner.reset()
    healer.code_agent.suggestions = []

    assert healer._heal_runtime() is False
