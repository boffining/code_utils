import pytest

from codehealer.agents.base_agent import BaseAgent


def test_base_agent_init_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        BaseAgent(repo_path="/tmp", system_prompt="test")


def test_query_llm_returns_content():
    agent = BaseAgent(repo_path="/tmp", system_prompt="system")
    agent.client.response_content = "hello world"
    response = agent._query_llm("user prompt")
    assert response == "hello world"


def test_query_llm_handles_errors():
    agent = BaseAgent(repo_path="/tmp", system_prompt="system")
    agent.client.raise_error = RuntimeError("boom")
    assert agent._query_llm("user prompt") == ""
