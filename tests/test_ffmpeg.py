import io
import pytest
import asyncio
import crawler.audio as audio_module
from crawler.audio import AudioCrawler
from config import Config


@pytest.mark.asyncio
async def test_FFmeg_init_url_empty():
    crawler = AudioCrawler(room_id=123, output_path="recordings/test.wav")
    crawler.url = None

    with pytest.raises(RuntimeError, match="url 为空"):
        await crawler.FFmpeg_init()


@pytest.mark.asyncio
async def test_FFmeg_init_already_initialized():
    crawler = AudioCrawler(room_id=123, output_path="recordings/test.wav")
    crawler.url = "http://example.com/stream"
    crawler.ffmpeg_process = object()

    with pytest.raises(RuntimeError, match="FFmpeg 已经初始化"):
        await crawler.FFmpeg_init()


@pytest.mark.asyncio
async def test_FFmeg_init_no_ffmpeg(monkeypatch):
    crawler = AudioCrawler(room_id=123, output_path="recordings/test.wav")
    crawler.url = "http://example.com/stream"

    # 模拟找不到 ffmpeg
    monkeypatch.setattr(audio_module.shutil, "which", lambda p: None)

    with pytest.raises(RuntimeError, match="未找到 ffmpeg 可执行文件"):
        await crawler.FFmpeg_init()


class _FakePopen:
    def __init__(self, poll_return=None, stderr_text=""):
        self._poll = poll_return
        self.pid = 4242
        self.stdout = io.StringIO("")
        self.stderr = io.StringIO(stderr_text)

    def poll(self):
        return self._poll


@pytest.mark.asyncio
async def test_FFmeg_init_process_crash(monkeypatch):
    crawler = AudioCrawler(room_id=123, output_path="recordings/test.wav")
    crawler.url = "http://example.com/stream"

    # 模拟找到 ffmpeg
    monkeypatch.setattr(audio_module.shutil, "which", lambda p: "/usr/bin/ffmpeg")

    # Popen 返回已退出的进程，stderr 有错误信息
    def fake_popen(*args, **kwargs):
        return _FakePopen(poll_return=1, stderr_text="fatal error")

    monkeypatch.setattr(audio_module.subprocess, "Popen", fake_popen)

    with pytest.raises(RuntimeError, match="FFmpeg 启动失败"):
        await crawler.FFmpeg_init()


@pytest.mark.asyncio
async def test_FFmeg_init_success(monkeypatch):
    crawler = AudioCrawler(room_id=123, output_path="recordings/test.wav")
    crawler.url = "http://example.com/stream"

    monkeypatch.setattr(audio_module.shutil, "which", lambda p: "/usr/bin/ffmpeg")

    # Popen 返回运行中的进程
    def fake_popen_running(*args, **kwargs):
        return _FakePopen(poll_return=None, stderr_text="")

    monkeypatch.setattr(audio_module.subprocess, "Popen", fake_popen_running)

    await crawler.FFmpeg_init()
    assert crawler.ffmpeg_process is not None
    assert crawler.ffmpeg_process.pid == 4242