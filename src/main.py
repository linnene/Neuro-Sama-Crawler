import sys
import asyncio
from config import config
from utils import setup_logger
from monitor import BilibiliMonitor
from crawler import DanmakuCrawler
from pipeline import APIClient

logger = setup_logger()

async def run():
    """Async entry point."""
    logger.info("Starting Neuro-sama Crawler...")
    
    # Initialize modules
    monitor = BilibiliMonitor()
    crawler = DanmakuCrawler()
    pipeline = APIClient(config.BACKEND_API_URL, config.BACKEND_API_TOKEN)
    
    logger.info(f"Monitoring rooms: {config.room_id}")
    
    # TODO: Main loop logic here
    # while True:
    #     for room in config.room_id:
    #         if await monitor.check_status(room):
    #             await crawler.start(room)

def main() -> int:
    """Main entry point of the application."""
    try:
        config.validate()
        asyncio.run(run())
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
