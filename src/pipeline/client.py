import os
import logging
from typing import Optional
from crawler.danmaku import DanmakuCrawler

from config import config

logger = logging.getLogger(__name__)

class APIClient:
    """
    负责将处理后的数据发送给后端
    """
    #感觉base_dir不需要传入
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.base_dir = config.BASE_DIR

        #管理爬虫生命周期
        self._active_crawlers: set[str] = set()

    def register_crawler(self, crawler: Optional[DanmakuCrawler]):
        """
        用于注册crawler,创建对应的文件写入句柄
        """
        if crawler is not None:
            os.makedirs(self.base_dir, exist_ok=True)
            path = os.path.join(self.base_dir, f"{crawler.room_id}.jsonl")

            f = open(path, "a", encoding="utf-8")
            crawler._file = f
            self._active_crawlers.add(crawler.room_id)
        

    async def on_crawler_stop(self, crawler:Optional[DanmakuCrawler]):
        """
        用于crawler停止时的回调
        """
        #TODO: Implement any finalization logic needed when crawler stops
        if crawler is not None:
            f = crawler._file
            if f:
                f.close()
            self._active_crawlers.discard(crawler.room_id)