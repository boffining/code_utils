import os
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DummyOpenAIResponse:
    def __init__(self, content):
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]


class DummyChatCompletions:
    def __init__(self, outer):
        self.outer = outer
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        if self.outer.raise_error:
            raise self.outer.raise_error
        return DummyOpenAIResponse(self.outer.response_content)


class DummyChat:
    def __init__(self, outer):
        self.completions = DummyChatCompletions(outer)


class DummyOpenAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.response_content = ""
        self.raise_error: Exception | None = None
        self.chat = DummyChat(self)


STUB_MODULE = types.ModuleType("openai")
STUB_MODULE.OpenAI = DummyOpenAI
sys.modules.setdefault("openai", STUB_MODULE)


@pytest.fixture
def temp_repo(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    return repo_path


@pytest.fixture(autouse=True)
def ensure_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    yield
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
