from .base import BaseMonitor
from config import config
import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BilibiliMonitor(BaseMonitor):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async def check_status(self, room_id: str):
        """
        检查直播状态
        live_status: 0=未开播, 1=直播中, 2=轮播
        """
        data = await self._fetch_room_data(room_id)
        if not data:
            return False
            
        is_live = data.get("live_status") == 1

        return is_live

    async def _fetch_room_data(self, room_id: str) -> Optional[Dict[str, Any]]:
        """
        内部辅助方法：请求 B 站 API 获取原始数据
        """
        try:
            async with httpx.AsyncClient(headers=self.HEADERS, timeout=10.0) as client:
                response = await client.get(config.BILIBILI_LIVE_API_URL, params={"room_id": room_id})
                response.raise_for_status()
                data = response.json()
                
                if data["code"] != 0:
                    logger.error(f"Bilibili API Error for room {room_id}: {data.get('msg', 'Unknown error')}")
                    return None
                
                return data["data"]
        except Exception as e:
            logger.error(f"Failed to fetch Bilibili room info: {e}")
            return None

    async def get_room_info(self, room_id: str) -> Dict[str, Any]:
        """
        获取清洗后的直播间信息
        """
        data = await self._fetch_room_data(room_id)
        if not data:
            return {}

        return {
            "platform": "bilibili",
            "room_id": str(data.get("room_id")),
            "title": data.get("title"),
            "live_status": data.get("live_status") == 1,
            "area_name": data.get("area_name"),
            "online": data.get("online"),
        }
