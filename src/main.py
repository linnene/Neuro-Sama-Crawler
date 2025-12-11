import sys
from config import config

def main() -> int:
    """Main entry point of the application."""
    try:
        config.validate()
        print(f"Hello from src/main.py!")
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
