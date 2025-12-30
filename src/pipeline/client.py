import os
import logging
import asyncio
from typing import Optional
from pathlib import Path
from crawler import DanmakuCrawler,AudioCrawler

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
        self.base_Output_dir = config.BASE_DIR
        self.base_Audio_dir = config.BASE_DIR


        #管理爬虫生命周期
        self._active_crawlers: set[str] = set()
        
        #管理音频爬虫生命周期
        self._active_Audiocrawlers: set[str] = set()

    

    def register_Audiocrawler(self, AudioCrawler:Optional[AudioCrawler]):
        if AudioCrawler is not None:
            os.makedirs(self.base_Output_dir, exist_ok=True)
        pass

    def register_crawler(self, crawler: Optional[DanmakuCrawler]):
        """
        用于注册crawler,创建对应的文件写入句柄
        """
        if crawler is not None:
            os.makedirs(self.base_Output_dir, exist_ok=True)
            path = os.path.join(self.base_Output_dir, f"{crawler.room_id}.jsonl")

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
            """
            调用 shell 脚本，将本地 output 目录中的数据推送出去
            """
            script_path = Path(config.PUSH_SCRIPT_PATH)

            if not script_path.exists():
                logger.error(f"Push script not found: {script_path}")
                return

            logger.info("Starting data push via shell script...")

            try:
                process = await asyncio.create_subprocess_exec(
                    str(script_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.error("Data push failed")
                    if stdout:
                        logger.error(stdout.decode())
                    if stderr:
                        logger.error(stderr.decode())
                else:
                    logger.info("Data push completed successfully")
                    if stdout:
                        logger.debug(stdout.decode())

            except Exception:
                logger.exception("Failed to execute push script")


