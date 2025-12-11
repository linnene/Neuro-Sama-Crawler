import os
from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Config:
    """
    manage application configuration from environment variables
    """
    
    # backend API configuration
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1/danmaku")
    BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN", "")

    # Live room configuration
    Bil_live_Root_url ="https://live.bilibili.com/"
    room_id = []

    @classmethod
    def validate(cls):
        """Validate required configuration variables."""
        required_vars = [
            "BACKEND_API_URL", 
            "BACKEND_API_TOKEN"
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


config = Config()
