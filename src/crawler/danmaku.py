
# coding=utf-8
from .base import BaseCrawler

from datetime import datetime

# 尝试导入 ZoneInfo，并准备好回退逻辑
from zoneinfo import ZoneInfo
import json
import logging
import asyncio
from zoneinfo import ZoneInfo
from selenium import webdriver
from typing import Optional,Callable, Awaitable,IO
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class DanmakuCrawler(BaseCrawler):
    """
    基于 Selenium 的弹幕爬虫实现
    """
    def __init__(self,room_id:str) -> None:
        self.room_id: str = room_id
        self._is_running = False
        self.driver = None
        self._file: IO | None = None
        self.is_registered: bool = False

        #用于爬虫停止时的回调
        self.on_stop: Optional[Callable[[str], Awaitable[None]]] = None

    async def start(self):
        self._is_running = True
        logger.info(f"Starting selenium danmaku crawler for room {self.room_id}")

        # 1. 初始化 headless Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # 2. 访问直播间页面
        url = f"https://live.bilibili.com/{self.room_id}"
        self.driver.get(url)
        logger.info(f"Opened {url}")

        # 3. 等待弹幕区加载
        await asyncio.sleep(5)

        # 用于去重的集合，存储当前已处理过的 data-ct
        seen_cts = set()

        try:
            while self._is_running:
                # Use JavaScript to directly extract all barrage data,
                # which is much more efficient than the Python loop find_element
                # 返回结构: [{'uname': 'xxx', 'content': 'xxx', 'ct': 'xxx'}, ...]
                script = """
                const items = document.querySelectorAll('#chat-items .danmaku-item');
                const result = [];
                for (const item of items) {
                    result.push({
                        uname: item.getAttribute('data-uname'),
                        content: item.getAttribute('data-danmaku'),
                        ct: item.getAttribute('data-ct')
                    });
                }
                return result;
                """
                
                try:
                    current_items = self.driver.execute_script(script)
                except Exception:
                    # 页面可能正在刷新或未加载完成
                    await asyncio.sleep(1)
                    continue

                new_danmaku_list = []
                current_cts = set()

                for item in current_items:
                    ct = item.get('ct')
                    # 记录当前页面上所有的 ct，用于更新 seen_cts
                    if ct:
                        current_cts.add(ct)
                    
                    # 如果是新弹幕（未在上一轮的 seen_cts 中）
                    if ct and ct not in seen_cts:
                        # 简单清洗
                        uname = item.get('uname', '').strip()
                        content = item.get('content', '').strip()
                        
                        if uname and content:
                            new_danmaku_list.append({
                                'username': uname,
                                'speaker': "chat",
                                'content': content,
                                'ct': ct
                            })

                # 处理新弹幕
                for danmaku in new_danmaku_list:
                    logger.info(f"[Room {self.room_id}] 弹幕: {danmaku['username']} : {danmaku['content']}")
                    # TODO: 直接写入文件，本地存储-[√]
                    await self.collect(danmaku, self.room_id)

                # 更新已处理集合
                seen_cts = current_cts

                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Danmaku crawler error: {e}")
        finally:
            await self.stop()
            if self.on_stop:
                await self.on_stop(self.room_id)

    async def stop(self):
        self._is_running = False
        logger.info("Stopping danmaku crawler")
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None


    async def collect(self, danmaku: dict, room_id: str):
        f = self._file
        if not f:
            logger.error(f"No file handle for crawler_id {room_id}")
            return
        
        # 使用安全的时区获取方法
        now_dt = get_shanghai_now()
        
        # 首次写入元数据
        if not getattr(self, "is_registered", False):
            try:
                meta = {
                    "event": "register",
                    "room_id": self.room_id,
                    "registered_at": now_dt.isoformat()
                }
                f.write(f"#META# {json.dumps(meta)}\n")
                f.flush()
                self.is_registered = True
            except Exception:
                logger.exception("Failed to write crawler registration metadata")

        # 过滤并写入弹幕
        to_write = {k: v for k, v in danmaku.items() if k != "ct"}
        to_write["data_ct"] = now_dt.isoformat()
        
        f.write(json.dumps(to_write, ensure_ascii=False) + "\n")
        f.flush()


def get_shanghai_now():
    try:
        return datetime.now(ZoneInfo("Asia/Shanghai"))
    except Exception:
        # 如果时区库缺失，记录一次警告并返回本地时间
        logger.warning("时区 Asia/Shanghai 未找到，已回退到本地时间。请安装 tzdata: pip install tzdata")
        return datetime.now().astimezone()