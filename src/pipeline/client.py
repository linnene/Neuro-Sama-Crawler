import os
import logging
import asyncio
from typing import Optional , Dict
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
        self.base_Output_dir = config.BASE_DIR / "danmaku_output"
        self.base_Audio_dir = config.BASE_DIR / "Audio_output"

        # 管理弹幕爬虫：room_id -> DanmakuCrawler
        self._active_crawlers: Dict[int, DanmakuCrawler] = {}
        
        # 管理音频爬虫：room_id -> AudioCrawler
        self._active_audio_crawlers: Dict[int, AudioCrawler] = {}

        # 启动后台监控任务
        self._monitor_task = asyncio.create_task(self._monitor_loop())

#------------------------------------------------------------------------------------------------------

    def register_Audiocrawler(self, adCrawler:Optional[AudioCrawler]):
        """
        用于注册AudioCrawler
        """
        #进程启动之后再注册，拿到FFmeg进程的id
        if adCrawler is not None:

            os.makedirs(self.base_Audio_dir, exist_ok=True)
            room_id = adCrawler.origin_room_id
            self._active_audio_crawlers[room_id] = adCrawler

            logger.info(f"AudioCrawler registered for room: {room_id}")

    def register_Danmakucrawler(self, dmCrawler: Optional[DanmakuCrawler]):
        """
        用于注册danmakuCrawler,创建对应的文件写入句柄
        """
        if dmCrawler is not None:
            os.makedirs(self.base_Output_dir, exist_ok=True)
            path = os.path.join(self.base_Output_dir, f"{dmCrawler.room_id}.jsonl")
            
            f = open(path, "a", encoding="utf-8")
            dmCrawler._file = f

            self._active_crawlers[int(dmCrawler.room_id)] = dmCrawler

    
    async def _monitor_loop(self):
        """
        检查所有 AudioCrawler 的进程健康度
        """
        try:
            while True:
                await asyncio.sleep(20)
                for room_id, crawler in list(self._active_audio_crawlers.items()):
                    if not crawler.is_healthy:
                        logger.error(f"监控发现房间 {room_id} 录制异常，尝试自动重启...")
                        # automatically restart the crawler
                        await self._restart_crawler(crawler)
                await asyncio.sleep(80) # 监控频率
        except Exception as e:
            logger.error(f"Health monitor loop error: {e}")
            await asyncio.sleep(5)  
        #TODO：添加对 DanmakuCrawler 健康度的轮询

#------------------------------------------------------------------------------------------------------

    async def on_crawler_stop(self,room_id: int):
        """
        用于crawler停止时的回调
        """
        if room_id in self._active_crawlers:
            dmCrawler = self._active_crawlers.pop(room_id)
            await dmCrawler.stop()

    async def on_audio_stop(self, room_id: int):
        """
        用于AudioCrawler停止时的回调
        """
        if room_id in self._active_audio_crawlers:
            adCrawler = self._active_audio_crawlers.pop(room_id)
            await adCrawler.stop()

    async def _restart_crawler(self, adCrawler: AudioCrawler):
        """重启策略"""
        try:
            logger.info(f"房间 {adCrawler.origin_room_id} 自动重启指令已发出")
            await adCrawler.stop()
            await asyncio.sleep(10)
            await adCrawler.start()
        except Exception as e:
            logger.error(f"自动重启房间 {adCrawler.origin_room_id} 失败: {e}")