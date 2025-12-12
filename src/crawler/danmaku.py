
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

        # 3. 等待弹幕区加载（可根据实际页面结构调整等待逻辑）
        await asyncio.sleep(5)  # 简单粗暴等待页面加载，后续可用WebDriverWait优化

        # 4. 定时抓取弹幕元素
        last_danmaku_set = set()
        from selenium.webdriver.common.by import By
        try:
            while self._is_running:
                # 适配B站弹幕DOM结构，提取用户名和弹幕内容
                danmaku_elements = self.driver.find_elements(
                    By.XPATH,
                    '//*[@id="chat-items"]/div[contains(@class, "danmaku-item")]'
                )

                new_danmaku = []
                for elem in danmaku_elements:
                    try:
                        username_elem = elem.find_element(By.CSS_SELECTOR, 'span.user-name')
                        content_elem = elem.find_element(By.CSS_SELECTOR, 'span.danmaku-item-right')
                        username = username_elem.text.strip().rstrip(':')
                        content = content_elem.text.strip()
                        # 用用户名+内容做唯一性去重
                        danmaku_key = f"{username}:{content}"
                        if content and danmaku_key not in last_danmaku_set:
                            new_danmaku.append({
                                'username': username,
                                'content': content
                            })
                            last_danmaku_set.add(danmaku_key)
                    except Exception:
                        continue

                for danmaku in new_danmaku:
                    logger.info(f"[Room {room_id}] 弹幕: {danmaku['username']} : {danmaku['content']}")

                # 控制弹幕缓存大小，防止内存泄漏
                if len(last_danmaku_set) > 5000:
                    last_danmaku_set = set(list(last_danmaku_set)[-1000:])

                await asyncio.sleep(1)
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
