import os

import pytest

from codehealer.agents.code_agent import CodeAgent


def test_code_agent_parses_valid_response(tmp_path):
    repo_path = tmp_path
    agent = CodeAgent(str(repo_path))
    expected_file = repo_path / "module.py"
    agent.client.response_content = (
        "FILEPATH: module.py\n" "```python\nprint('hello')\n```"
    )
    suggestion = agent.get_suggestion("Traceback")
    assert suggestion == (os.path.normpath(str(expected_file)), "print('hello')")


def test_code_agent_rejects_invalid_format():
    agent = CodeAgent("/tmp")
    agent.client.response_content = "unexpected"
    assert agent.get_suggestion("Traceback") is None


def test_parse_response_rejects_outside_repo(tmp_path, capsys):
    repo_path = tmp_path
    agent = CodeAgent(str(repo_path))
    response = "FILEPATH: ../secrets.py\n```python\nprint('hi')\n```"
    assert agent._parse_response(response) is None
    captured = capsys.readouterr()
    assert "outside the repository" in captured.out
