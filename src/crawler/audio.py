from .base import BaseAudioCrawler
import logging
import aiohttp
import asyncio

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

    async def start(self) -> dict:
        """
        start 的 Docstring
        
        :param self: 说明
        """
        if self.is_running:
            logger.warning("Audio crawler is already running")
            return {}
        

        if self.room_id is None:
            await self.fetch_room_id()

        # fetch_flv_avc_stream 是 coroutine，需要 await
        json_out = await self.fetch_flv_avc_stream()

        self.is_running = True

        return json_out
    
    async def stop(self):
        pass


    async def fetch_room_id(self) -> None:
        """
        fetch_room_id 的 Docstring
        
        :param self: 说明
        """
        url = "https://api.live.bilibili.com/room/v1/Room/get_info"
        params = {"room_id": self.origin_room_id}

        data = await self._fetch_json(url, params)

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

        data = await self._fetch_json(url, params)

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
                    
                    URL = first["host"] + codec["base_url"] + first["extra"]

                    print("URL:", URL)
                    
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

    async def _fetch_json(self, url: str, params: dict | None = None, max_retries: int = 3, timeout: int = 10) -> dict:
        """
        使用带浏览器头的请求去获取 JSON，包含重试和退避策略，减少被 WAF/反爬阻断（如 412）的问题。
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": f"https://live.bilibili.com/{self.origin_room_id}",
            "Origin": "https://live.bilibili.com",
        }

        attempt = 0
        while attempt < max_retries:
            attempt += 1
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                    async with session.get(url, params=params, headers=headers) as resp:
                        text = await resp.text()
                        if resp.status != 200:
                            logger.warning("Request to %s returned status %s (attempt %d/%d): %s", url, resp.status, attempt, max_retries, text[:200])
                            # 对 4xx/5xx 做重试（可根据需要调整）
                            if attempt >= max_retries:
                                raise RuntimeError(f"HTTP 请求失败，状态码: {resp.status}")
                            await asyncio.sleep(1 + attempt)
                            continue

                        try:
                            return await resp.json()
                        except Exception:
                            # 如果解析 JSON 失败，抛出包含文本的异常以便诊断
                            raise RuntimeError(f"无法解析 JSON 响应: {text[:500]}")

            except Exception as exc:
                logger.warning("请求 %s 出错 (attempt %d/%d): %s", url, attempt, max_retries, exc)
                if attempt >= max_retries:
                    raise
                await asyncio.sleep(1 + attempt)

        raise RuntimeError("达到最大重试次数但未成功获取数据")