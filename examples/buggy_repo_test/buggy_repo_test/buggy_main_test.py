from .main import greet

def test_greet():
    """This test should pass after the agent corrects the function name."""
    assert greet("World") == "Hello, World!"
