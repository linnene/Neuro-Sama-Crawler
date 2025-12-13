from .base import BaseAudioCrawler
import logging
import aiohttp

logger = logging.getLogger(__name__)

class AudioCrawler(BaseAudioCrawler):
    """
    Bilibili 音频爬虫
    负责从 B 站直播间获取音频流
    """

    def __init__(self, room_id: int) -> None:
        self.origin_room_id: int = room_id   # 用户传入的
        self.room_id: int | None = None      # 规范化后的真实 room_id
        self.is_running: bool = False

    async def start(self):
        """
        start 的 Docstring
        
        :param self: 说明
        """
        if self.is_running:
            return

        if self.room_id is None:
            await self.fetch_room_id()
        
        json_out = self.fetch_flv_avc_stream()

        self.is_running = True

    async def stop(self):
        pass


    async def fetch_room_id(self) -> None:
        """
        fetch_room_id 的 Docstring
        
        :param self: 说明
        """
        url = "https://api.live.bilibili.com/room/v1/Room/get_info"
        params = {"room_id": self.origin_room_id}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP 请求失败，状态码: {resp.status}")
                data = await resp.json()

        if data.get("code") != 0:
            raise RuntimeError(f"接口返回错误: {data.get('msg')}")

        room_info = data.get("data")
        if not room_info or "room_id" not in room_info:
            raise RuntimeError("返回数据中缺少 room_id")

        self.room_id = int(room_info["room_id"])
    

    async def fetch_flv_avc_stream(self) -> dict:
        """
        查询直播播放信息，并返回最小可用的 FLV + AVC 流信息
        """
        url = "https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo"
        params = {
            "room_id": self.room_id,
            "no_playurl": 0,
            "mask": 1,
            "qn": 0,
            "platform": "web",
            "protocol": "0,1",
            "format": "0,2",
            "codec": "0,1",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP 请求失败，状态码: {resp.status}")
                data = await resp.json()

        if data.get("code") != 0:
            raise RuntimeError(f"接口返回错误: {data.get('message')}")

        streams = (
            data
            .get("data", {})
            .get("playurl_info", {})
            .get("playurl", {})
            .get("stream", [])
        )

        for stream in streams:
            if stream.get("protocol_name") != "http_stream":
                continue

            for fmt in stream.get("format", []):
                if fmt.get("format_name") != "flv":
                    continue

                for codec in fmt.get("codec", []):
                    if codec.get("codec_name") != "avc":
                        continue

                    url_info = codec.get("url_info")
                    if not url_info:
                        continue

                    first = url_info[0]

                    return {
                        "protocol": "http_stream",
                        "format": "flv",
                        "codec": "avc",
                        "host": first["host"],
                        "base_url": codec["base_url"],
                        "extra": first["extra"],
                    }

        raise RuntimeError("未找到可用的 http_stream + flv + avc 播放流")


    async def get_audio_stream(self):
        """
        获取音频流的异步生成器
        :yield: 音频数据块

        1. 用异步 HTTP 持续读取字节流
        """
        yield b""  