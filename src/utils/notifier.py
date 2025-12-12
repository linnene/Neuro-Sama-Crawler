import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AudioServiceNotifier:
    def __init__(self, service_url: Optional[str]):
        self.service_url = service_url
        self.client = httpx.AsyncClient(timeout=5.0)

    async def notify(self, room_id: str, action: str) -> bool:
        """
        Notify the audio service to start or stop recording.
        
        Args:
            room_id: The room ID to record.
            action: "start" or "stop".
            
        Returns:
            True if notification was successful or no service configured, False otherwise.
        """
        if not self.service_url:
            logger.debug("No AUDIO_SERVICE_URL configured, skipping notification.")
            return True

        payload = {
            "room_id": room_id,
            "action": action,
            "platform": "bilibili"
        }

        try:
            logger.info(f"Notifying Audio Service: {action} recording for room {room_id}")
            response = await self.client.post(self.service_url, json=payload)
            response.raise_for_status()
            logger.info(f"Audio Service notified successfully: {response.status_code}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to notify Audio Service: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error notifying Audio Service: {e}")
            return False

    async def close(self):
        await self.client.aclose()
