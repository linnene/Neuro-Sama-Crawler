import os
import logging
from typing import Optional
from crawler.danmaku import DanmakuCrawler

from config import config

logger = logging.getLogger(__name__)

class APIClient:
    """
    负责管理爬虫文件写入句柄生命周期，以及与外部 API 的交互
    """
    #感觉base_dir不需要传入
    def __init__(self):
        #暂时注销
        # self.api_url = api_url
        
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

            # 写入注册元信息：注册时间和房间号，便于后续审计
            try:
                from datetime import datetime
                meta = {
                    "event": "register",
                    "room_id": crawler.room_id,
                    "registered_at": datetime.now().isoformat()
                }
                f.write("#META# " + ("%s\n" % (meta)) )
                f.flush()
            except Exception:
                logger.exception("Failed to write crawler registration metadata")

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
            crawler.stop

    async def send_data(self):
        #TODO: 可以决定是否启用，自动每天结束之后，将收集的所有数据发送到后端API
        #可以编写shell使用scp
        pass
