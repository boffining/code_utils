from codehealer.agents.environment_agent import EnvironmentAgent


def test_environment_agent_returns_str(temp_repo):
    agent = EnvironmentAgent(str(temp_repo))
    agent.client.response_content = "flask==2.3.2"
    suggestion = agent.get_suggestion("error log", "flask==0.1")
    assert suggestion == "flask==2.3.2"
