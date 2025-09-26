def greet(name: str) -> str:
    """A simple function with a deliberate typo for the agent to fix."""
    # The agent should correct this to "Hello"
    return f"Helo, {name}!"

def main():
    """Entry point for the buggy application."""
    print(gree("World"))
    print(Path(".".strip()))  # Path is missing on purpose

if __name__ == "__main__":
    main()
    
