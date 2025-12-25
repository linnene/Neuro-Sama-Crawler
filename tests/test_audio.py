import pytest
import re
from aioresponses import aioresponses
from crawler.audio import AudioCrawler

@pytest.mark.asyncio
async def test_fetch_room_id_success():
    crawler = AudioCrawler(room_id=123456)
    mock_json = {
        "code": 0,
        "msg": "ok",
        "data": {"room_id": 654321}
    }

    with aioresponses() as m:
        m.get(
            re.compile(r"https://api\.live\.bilibili\.com/room/v1/Room/get_info.*"),
            payload=mock_json
        )

        await crawler.fetch_room_id()
        assert crawler.room_id == 654321


@pytest.mark.asyncio
async def test_fetch_room_id_api_error():
    crawler = AudioCrawler(room_id=123456)
    mock_json = {"code": 1, "msg": "房间不存在"}

    with aioresponses() as m:
        m.get(
            re.compile(r"https://api\.live\.bilibili\.com/room/v1/Room/get_info.*"),
            payload=mock_json
        )

        with pytest.raises(RuntimeError, match="接口返回错误"):
            await crawler.fetch_room_id()


@pytest.mark.asyncio
async def test_fetch_flv_avc_stream_success():
    crawler = AudioCrawler(room_id=123456)
    crawler.room_id = 654321  # 直接设置真实 room_id，跳过 fetch_room_id

    mock_json = {
        "code": 0,
        "message": "0",
        "data": {
            "playurl_info": {
                "playurl": {
                    "stream": [
                        {
                            "protocol_name": "http_stream",
                            "format": [
                                {
                                    "format_name": "flv",
                                    "codec": [
                                        {
                                            "codec_name": "avc",
                                            "base_url": "/live-bvc/123/live.flv?",
                                            "url_info": [
                                                {"host": "https://example.com", "extra": "token=abc"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

    with aioresponses() as m:
        m.get(
           re.compile(r"https://api\.live\.bilibili\.com/xlive/web-room/v2/index/getRoomPlayInfo.*"),
            payload=mock_json
        )

        stream_info = await crawler.fetch_flv_avc_stream()
        if not stream_info:
            pytest.fail("Expected stream_info, got empty dict")
        assert stream_info["protocol"] == "http_stream"
        assert stream_info["format"] == "flv"
        assert stream_info["codec"] == "avc"
        assert stream_info["host"] == "https://example.com"
        assert stream_info["base_url"] == "/live-bvc/123/live.flv?"
        assert stream_info["extra"] == "token=abc"


@pytest.mark.asyncio
async def test_fetch_flv_avc_stream_not_found():
    crawler = AudioCrawler(room_id=123456)
    crawler.room_id = 654321  # 直接设置真实 room_id

    # 返回空 stream
    mock_json = {"code": 0, "message": "0", "data": {"playurl_info": {"playurl": {"stream": []}}}}

    with aioresponses() as m:
        m.get(
            re.compile(r"https://api\.live\.bilibili\.com/xlive/web-room/v2/index/getRoomPlayInfo.*"),
            payload=mock_json
        )

        with pytest.raises(RuntimeError, match="未找到可用的 http_stream"):
            await crawler.fetch_flv_avc_stream()
