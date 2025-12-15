import os
from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Config:
    """
    manage application configuration from environment variables
    """
    # Output base directory
    BASE_DIR = ROOT_DIR / "output"

    # backend API configuration
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1/danmaku")

    # Live room configuration
    BILIBILI_LIVE_API_URL = "https://api.live.bilibili.com/room/v1/Room/get_info"
    BILIBILI_ROOM_IDS = os.getenv("BILIBILI_ROOM_IDS", "").split(",") if os.getenv("BILIBILI_ROOM_IDS") else []

    @classmethod
    def validate(cls):
        """Validate required configuration variables."""
        required_vars = [
            "BACKEND_API_URL"
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


config = Config()
