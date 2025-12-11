from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any

class BaseCrawler(ABC):
    """
    爬虫基类
    负责连接直播间并获取原始数据流
    """
    
    @abstractmethod
    async def start(self, room_id: str):
        """启动爬取任务"""
        pass

    @abstractmethod
    async def stop(self):
        """停止爬取任务"""
        pass
