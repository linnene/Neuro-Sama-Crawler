import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class APIClient:
    """
    负责将处理后的数据发送给后端
    """
    
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.token = token
        self._queue = []

    async def send_batch(self, data_batch: List[Dict[str, Any]]):
        """
        批量发送数据
        """
        # TODO: Implement HTTP POST request
        logger.info(f"Sending batch of {len(data_batch)} items to {self.api_url}")
        pass
