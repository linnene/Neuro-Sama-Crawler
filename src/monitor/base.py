from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMonitor(ABC):
    """
    直播间监控基类
    负责检查直播间状态（是否开播）
    """
    
    @abstractmethod
    async def check_status(self, room_id: str) -> bool:
        """
        检查指定房间是否正在直播
        :param room_id: 房间号
        :return: True if live, False otherwise
        """
        pass

    @abstractmethod
    async def get_room_info(self, room_id: str) -> Dict[str, Any]:
        """
        获取直播间详细信息
        """
        pass
