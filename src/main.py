import sys
import asyncio
from typing import Dict
from config import config
from utils import setup_logger
from utils.notifier import AudioServiceNotifier
from monitor import BilibiliMonitor
from crawler import DanmakuCrawler
from pipeline import APIClient

logger = setup_logger()

async def run():
    """Async entry point."""
    logger.info("Starting Neuro-sama Crawler...")
    
    # Initialize modules
    monitor = BilibiliMonitor()
    
    # Initialize notifier only if enabled and URL is configured
    audio_url = config.AUDIO_SERVICE_URL if config.ENABLE_AUDIO_SERVICE else None
    if audio_url:
        logger.info(f"Audio Service integration ENABLED. Webhook: {audio_url}")
    else:
        logger.info("Audio Service integration DISABLED.")
        
    notifier = AudioServiceNotifier(audio_url)
    # pipeline = APIClient(config.BACKEND_API_URL, config.BACKEND_API_TOKEN) # TODO: Pass to crawler
    
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
                        if room_id not in active_sessions:
                            logger.info(f"Room {room_id} is LIVE! Starting services...")
                            
                            # 1. Notify Audio Service
                            await notifier.notify(room_id, "start")
                            
                            # 2. Start Danmaku Crawler
                            crawler = DanmakuCrawler()
                            # TODO: Pass pipeline to crawler
                            # crawler.pipeline = pipeline 
                            
                            task = asyncio.create_task(crawler.start(room_id))
                            
                            active_sessions[room_id] = {
                                'crawler': crawler,
                                'task': task
                            }
                    else:
                        if room_id in active_sessions:
                            logger.info(f"Room {room_id} went OFFLINE. Stopping services...")
                            
                            # 1. Stop Danmaku Crawler
                            session = active_sessions.pop(room_id)
                            crawler = session['crawler']
                            task = session['task']
                            
                            await crawler.stop()
                            try:
                                await task
                            except asyncio.CancelledError:
                                pass
                                
                            # 2. Notify Audio Service
                            await notifier.notify(room_id, "stop")
                            
                except Exception as e:
                    logger.error(f"Error monitoring room {room_id}: {e}")
            
            # Wait before next poll
            await asyncio.sleep(60)
            
    except asyncio.CancelledError:
        logger.info("Stopping main loop...")
    finally:
        # Cleanup
        for room_id, session in active_sessions.items():
            await session['crawler'].stop()
            await notifier.notify(room_id, "stop")
        await notifier.close()

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
