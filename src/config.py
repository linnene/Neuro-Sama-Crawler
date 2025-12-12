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
    BILIBILI_LIVE_API_URL = "https://api.live.bilibili.com/room/v1/Room/get_info"
    BILIBILI_ROOM_IDS = os.getenv("BILIBILI_ROOM_IDS", "").split(",") if os.getenv("BILIBILI_ROOM_IDS") else []

    # External Service Webhooks
    # URL to notify when recording should start/stop (e.g., the Audio Worker service)
    AUDIO_SERVICE_URL = os.getenv("AUDIO_SERVICE_URL")
    # Master switch for audio service notification (default: True if URL is set)
    ENABLE_AUDIO_SERVICE = os.getenv("ENABLE_AUDIO_SERVICE", "true").lower() == "true"

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
