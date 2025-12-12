import pytest
import asyncio
from unittest.mock import patch, MagicMock
from crawler.danmaku import DanmakuCrawler

@pytest.mark.asyncio
async def test_crawler_lifecycle():
    # Mock 掉 webdriver，避免真实启动浏览器
    with patch('crawler.danmaku.webdriver.Chrome') as mock_chrome, \
         patch('crawler.danmaku.ChromeDriverManager') as mock_manager:
        
        # 设置 Mock 返回值
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        crawler = DanmakuCrawler()
        assert crawler._is_running is False
        
        # 启动爬虫的任务
        task = asyncio.create_task(crawler.start("123456"))
        
        # 让它运行一小会儿
        # 因为 start 中有 await asyncio.sleep(5)，所以这里 sleep 0.1 会让 start 跑到第一个 await 处挂起
        await asyncio.sleep(0.1)
        
        # 验证状态
        assert crawler._is_running is True
        # 验证是否调用了浏览器初始化
        mock_chrome.assert_called_once()
        mock_driver.get.assert_called_with("https://live.bilibili.com/123456")
        
        # 停止爬虫
        await crawler.stop()
        assert crawler._is_running is False
        
        # 取消任务以清理
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
