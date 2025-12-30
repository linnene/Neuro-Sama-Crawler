import sys
import asyncio
from typing import Dict
from config import config
from utils import setup_logger
from monitor import BilibiliMonitor
from crawler import DanmakuCrawler, AudioCrawler
from pipeline import APIClient

logger = setup_logger()

async def run():
    """Async entry point."""
    logger.info("Starting Neuro-sama Crawler...")
    
    # Initialize modules
    monitor = BilibiliMonitor()
    cilent = APIClient()
    
    # State management
    # room_id -> {'crawler': DanmakuCrawler, 'task': asyncio.Task}
    active_sessions: Dict[str, dict] = {}
    
    rooms = config.BILIBILI_ROOM_IDS
    if not rooms:
        logger.warning("No rooms configured to monitor! Set BILIBILI_ROOM_IDS in .env")
        return

    logger.info(f"Monitoring rooms: {rooms}")
    
    try:
        while True:
            for room_id in rooms:
                try:
                    is_live = await monitor.check_status(room_id)
                    
                    if is_live:
                        #TODO:更改爬虫生命周期管理逻辑，使用APIClient管理
                        if room_id not in active_sessions:
                            logger.info(f"Room {room_id} is LIVE! Starting services...")
                            
                            # Start Danmaku Crawler
                            crawler = DanmakuCrawler(room_id)
                            # TODO: Pass pipeline to crawler
                            cilent.register_Danmakucrawler(crawler)
                            
                            task = asyncio.create_task(crawler.start())
                            
                            active_sessions[room_id] = {
                                'crawler': crawler,
                                'task': task
                            }
                    else:
                        if room_id in active_sessions:
                            logger.info(f"Room {room_id} went OFFLINE. Stopping services...")
                            
                            # Stop Danmaku Crawler
                            session = active_sessions.pop(room_id)
                            crawler = session['crawler']
                            task = session['task']
                            
                            await cilent.on_crawler_stop(crawler)
                            task.cancel()
                            try:
                                await task
                            except asyncio.CancelledError:
                                pass
                            
                except Exception as e:
                    logger.error(f"Error monitoring room {room_id}: {e}")
            
            # Wait before next poll
            await asyncio.sleep(60)
            
    except asyncio.CancelledError:
        logger.info("Stopping main loop...")
    finally:
        # Cleanup
        for room_id, session in active_sessions.items():
            await cilent.on_crawler_stop(session['crawler'])

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
