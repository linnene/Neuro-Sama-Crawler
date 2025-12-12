import asyncio
import logging
import sys
import os

# 确保能导入 src 下的模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from crawler.danmaku import DanmakuCrawler

# 配置日志输出到标准输出，方便 Docker logs 查看
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def main():
    # 默认房间号 6 (B站官方直播间)，也可通过命令行参数传入
    room_id = sys.argv[1] if len(sys.argv) > 1 else "6"
    
    logger.info(f"Starting Docker test for room: {room_id}")
    logger.info("Crawler is running in headless mode (default).")
    logger.info("Logs will be printed below:")
    
    crawler = DanmakuCrawler()
    
    try:
        await crawler.start(room_id)
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await crawler.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
