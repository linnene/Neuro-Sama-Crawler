import sys
import asyncio
from typing import Dict
from config import config
from utils import setup_logger
from monitor import BilibiliMonitor
from crawler import DanmakuCrawler, AudioCrawler
from pipeline import APIClient

logger = setup_logger()

# --- 辅助逻辑抽离 ---

async def start_room_services(room_id: str, cilent, active_sessions: Dict):
    """启动指定房间的弹幕和音频服务"""
    logger.info(f"Room {room_id} is LIVE! Starting services...")
    
    # 1. 初始化弹幕爬虫
    danmaku_crawler = DanmakuCrawler(room_id)
    cilent.register_Danmakucrawler(danmaku_crawler)
    d_task = asyncio.create_task(danmaku_crawler.start())

    # 2. 初始化音频爬虫
    audio_output_path = config.BASE_DIR / "Audio_output"
    audio_crawler = AudioCrawler(int(room_id), audio_output_path)
    cilent.register_Audiocrawler(audio_crawler)
    a_task = asyncio.create_task(audio_crawler.start())
    
    active_sessions[room_id] = {
        'danmaku': danmaku_crawler,
        'audio': audio_crawler,
        'tasks': [d_task, a_task]
    }

async def stop_room_services(room_id: str, cilent, active_sessions: Dict):
    """停止指定房间的所有服务并清理任务"""
    if room_id not in active_sessions:
        return
        
    logger.info(f"Room {room_id} went OFFLINE. Stopping services...")
    session = active_sessions.pop(room_id)
    
    # 停止爬虫并移除句柄/监控
    await cilent.on_crawler_stop(int(room_id))
    await cilent.on_audio_stop(int(room_id))
    
    # 取消并回收异步任务
    for t in session['tasks']:
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass

# --- 主逻辑 ---

async def run():
    """Async entry point."""
    logger.info("Starting Neuro-sama Crawler...")
    
    monitor = BilibiliMonitor()
    cilent = APIClient()
    active_sessions: Dict[str, dict] = {}
    
    rooms = config.BILIBILI_ROOM_IDS
    if not rooms:
        logger.warning("No rooms configured! Set BILIBILI_ROOM_IDS in .env")
        return

    logger.info(f"Monitoring rooms: {rooms}")
    
    try:
        while True:
            for room_id in rooms:
                try:
                    is_live = await monitor.check_status(room_id)
                    
                    if is_live and room_id not in active_sessions:
                        logger.info(f"Room {room_id} is aLIVE-[✔]")
                        await start_room_services(room_id,cilent,active_sessions)
                        
                    elif not is_live and room_id in active_sessions:
                        await stop_room_services(room_id,cilent, active_sessions)
                            
                except Exception as e:
                    logger.error(f"Error monitoring room {room_id}: {e}")
            
            await asyncio.sleep(60)
            
    except asyncio.CancelledError:
        logger.info("Stopping main loop...")
    finally:
        logger.info("Cleaning up all active sessions...")
        # 退出时清理所有房间
        for room_id in list(active_sessions.keys()):
            await stop_room_services(room_id, cilent, active_sessions)

def main() -> int:
    """Main entry point."""
    try:
        config.validate()
        asyncio.run(run())
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        # KeyboardInterrupt 会被 asyncio.run 捕获并转化为正常退出过程
        pass 
    return 0

if __name__ == "__main__":
    sys.exit(main())