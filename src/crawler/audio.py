from .base import BaseAudioCrawler
import logging
import aiohttp
import asyncio
import subprocess
import shutil

from pathlib import Path

logger = logging.getLogger(__name__)

class AudioCrawler(BaseAudioCrawler):
    """
    Bilibili 音频爬虫
    负责从 B 站直播间获取音频流
    """
#------------------------------------------------------------------------------

    def __init__(self, room_id: int, output_path:Path) -> None:
        self.origin_room_id: int = room_id   # 用户传入的
        self.room_id: int | None = None      # 规范化后的真实 room_id
        self.is_running: bool = False
        self.output_path = output_path

        # 临时流url
        self.url = None

        self.ffmpeg_process: subprocess.Popen | None = None
        self.ffmpeg_path: str = "D:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"  # 或者绝对路径
        

    async def start(self) -> None:
        """
        start 的 Docstring
        
        :param self: 说明
        """

        if self.is_running:
            logger.warning("Audio crawler is already running")
            return 
        
        if self.room_id is None:
            await self.fetch_room_id()

        # fetch_flv_avc_stream 是 coroutine，需要 await
        json_out = await self.fetch_flv_avc_stream()
        # 临时流url
        if json_out:
            self.url = json_out["host"] + json_out["base_url"] + json_out["extra"]
        else:
            return 
        await self.FFmpeg_init()
        self.is_running = True
        return 
    
    async def stop(self):
        self.is_running = False
        await self.FFmpeg_stop()

#------------------------------------------------------------------------------


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

        if data.get("data",{}).get("playurl_info", {}):
            streams = (
                data
                .get("data", {})
                .get("playurl_info", {})
                .get("playurl", {})
                .get("stream", [])
            )
        else:
            logger.error("获取播放信息失败，可能直播未开播或房间不存在")
            return {}


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
                            if resp:
                                return await resp.json()
                            else:
                                raise RuntimeError("没有响应内容")
                        except Exception:
                            # 如果解析 JSON 失败，抛出包含文本的异常以便诊断
                            raise RuntimeError(f"无法解析 JSON 响应: {text[:500]}")

            except Exception as exc:
                logger.warning("请求 %s 出错 (attempt %d/%d): %s", url, attempt, max_retries, exc)
                if attempt >= max_retries:
                    raise
                await asyncio.sleep(1 + attempt)

        raise RuntimeError("达到最大重试次数但未成功获取数据")
    

    async def FFmpeg_init(self):

        output_path = self.prepare_output_path("wav")

        if not self.url:
            raise RuntimeError("FFmpeg 初始化失败：url 为空")

        if getattr(self, "ffmpeg_process", None) is not None:
            raise RuntimeError("FFmpeg 已经初始化")

        # 1. 校验 ffmpeg 是否存在
        if shutil.which(getattr(self, "ffmpeg_path", "ffmpeg")) is None:
            raise RuntimeError(f"未找到 ffmpeg 可执行文件: {getattr(self, 'ffmpeg_path', 'ffmpeg')}")

        # 2. 设置 HTTP headers 避免 403
        headers = (
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\r\n"
            f"Referer: https://live.bilibili.com/{self.origin_room_id}\r\n"
        )

        cmd = [
            self.ffmpeg_path,
            "-loglevel", "info",
            "-fflags", "nobuffer",
            "-headers", headers,
            "-i", self.url,

            "-map", "0:a:0",
            "-acodec", "pcm_s16le",
            "-ar", "48000",
            
            str(output_path)
        ]

        logger.info("启动 FFmpeg: %s", " ".join(cmd))

        # 3. 启动子进程（非阻塞）
        self.ffmpeg_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 4. 给 FFmpeg 一点时间判断它是否秒崩
        await asyncio.sleep(1)

        if self.ffmpeg_process.poll() is not None:
            stderr = self.ffmpeg_process.stderr.read()
            self.ffmpeg_process = None
            raise RuntimeError(f"FFmpeg 启动失败:\n{stderr}")

        logger.info("FFmpeg 初始化成功，进程 PID=%s", self.ffmpeg_process.pid)


    async def FFmpeg_stop(self) -> None:

        """
        释放 FFmpeg 资源
        终止子进程
        """

        proc = getattr(self, "ffmpeg_process", None)
        if proc is None:
            return

        logger.info("正在停止 FFmpeg，PID=%s", proc.pid)

        # 如果已经退出，直接清理
        if proc.poll() is not None:
            self.ffmpeg_process = None
            return

        # 1. 尝试优雅退出
        try:
            proc.terminate()
        except Exception as e:
            logger.warning("FFmpeg terminate 失败: %s", e)

        # 2. 等待一小段时间
        try:
            await asyncio.wait_for(
                asyncio.to_thread(proc.wait),
                timeout=3
            )
        except asyncio.TimeoutError:
            logger.warning("FFmpeg 未在超时内退出，强制 kill，PID=%s", proc.pid)
            try:
                proc.kill()
            except Exception as e:
                logger.error("FFmpeg kill 失败: %s", e)

        # 3. 回收管道，避免资源泄漏
        try:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
        except Exception:
            pass

        self.ffmpeg_process = None
        logger.info("FFmpeg 已停止")

    def prepare_output_path(self, suffix: str = "wav") -> Path:

        path = self.output_path / f"room_{self.origin_room_id}.{suffix}"

        return path
