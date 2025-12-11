import sys
import os

# Add src to the path so we can import modules from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import main
from config import config

def test_config_validation():
    # Test that validation passes with mock env vars
    # We can mock os.environ or just check default values if they exist
    # For now, let's just check that the config object exists
    assert hasattr(config, 'BACKEND_API_URL')

def test_main_output(capsys, monkeypatch):
    # Mock necessary environment variables to pass validation
    monkeypatch.setenv("BACKEND_API_URL", "http://test.com")
    monkeypatch.setenv("BACKEND_API_TOKEN", "test_token")

    # This is a basic test to ensure main runs. 
    # In a real app, you'd test specific functions, not just the main entry point.
    try:
        main()
    except SystemExit:
        pass
    
    captured = capsys.readouterr()
    assert "Hello from src/main.py!" in captured.out
