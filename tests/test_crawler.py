import pytest
import asyncio
from crawler.danmaku import DanmakuCrawler

@pytest.mark.asyncio
async def test_crawler_lifecycle():
    crawler = DanmakuCrawler()
    assert crawler._is_running is False
    
    # 启动爬虫的任务
    task = asyncio.create_task(crawler.start("123456"))
    
    # 让它运行一小会儿
    await asyncio.sleep(0.1)
    assert crawler._is_running is True
    
    # 停止爬虫
    await crawler.stop()
    assert crawler._is_running is False
    
    # 等待任务结束
    await task
