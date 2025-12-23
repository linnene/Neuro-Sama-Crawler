from crawler import AudioCrawler
import asyncio
from config import config
import aiohttp
import asyncio
import subprocess

def play_live(url: str):
    subprocess.run([
        "ffplay",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-infbuf",
        url
    ])

async def test_flv_url(url: str, timeout=10):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": "https://live.bilibili.com/",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, timeout=timeout) as resp:
                print("HTTP 状态码:", resp.status)

                if resp.status != 200:
                    return False, "HTTP 非 200"

                # 读取 FLV 头（FLV header 至少 9 字节）
                header = await resp.content.readexactly(9)

                if not header.startswith(b"FLV"):
                    return False, "不是 FLV 流"

                # 再读一点数据，确认是活流
                chunk = await resp.content.read(1024)
                if not chunk:
                    return False, "FLV 无后续数据"

                return True, "FLV 直播流可用"

        except asyncio.TimeoutError:
            return False, "请求超时"
        except Exception as e:
            return False, f"异常: {e}"



async def main():
    for room_id in config.BILIBILI_ROOM_IDS:
        audio_crawler = AudioCrawler(int(room_id))
        msg = await audio_crawler.start()

        url = msg["host"] + msg["base_url"] + msg["extra"]

        play_live(url)

        ok, reason = await test_flv_url(url)
        print(f"房间 {room_id}: {reason}")

if __name__ == "__main__":
    asyncio.run(main())

