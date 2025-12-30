import asyncio
from config import config
from crawler.audio import AudioCrawler
from utils import setup_logger



logger = setup_logger()


async def main():
    room_ids = config.BILIBILI_ROOM_IDS
    for room_id in room_ids:
        crawler = AudioCrawler(room_id=int(room_id), output_path =config.Audio_output_DIR)
        dict = await crawler.start()
        

if __name__ == "__main__":
    asyncio.run(main())
    while True:
        pass