
# coding=utf-8
from .base import BaseCrawler

import logging
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class DanmakuCrawler(BaseCrawler):
    """
    基于 Selenium 的弹幕爬虫实现
    """
    def __init__(self):
        self._is_running = False
        self.driver = None

    async def start(self, room_id: str):
        self._is_running = True
        logger.info(f"Starting selenium danmaku crawler for room {room_id}")
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
        url = f"https://live.bilibili.com/{room_id}"
        self.driver.get(url)
        logger.info(f"Opened {url}")

        # 3. 等待弹幕区加载
        await asyncio.sleep(5)

        # 用于去重的集合，存储当前已处理过的 data-ct
        seen_cts = set()

        try:
            while self._is_running:
                # 使用 JavaScript 直接提取所有弹幕数据，效率远高于 Python 循环 find_element
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
                                'content': content,
                                'ct': ct
                            })

                # 处理新弹幕
                for danmaku in new_danmaku_list:
                    logger.info(f"[Room {room_id}] 弹幕: {danmaku['username']} : {danmaku['content']}")
                    # TODO: 这里调用 pipeline 发送数据到后端
                    # await self.pipeline.send(danmaku)

                # 更新已处理集合
                seen_cts = current_cts

                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Danmaku crawler error: {e}")
        finally:
            self.stop_driver()

    async def stop(self):
        self._is_running = False
        logger.info("Stopping danmaku crawler")
        self.stop_driver()

    def stop_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
