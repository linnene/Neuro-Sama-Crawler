import pytest
from unittest.mock import patch, MagicMock
from pipeline.client import APIClient

@pytest.fixture
def api_client():
    return APIClient("http://test.api", "test_token")

def test_client_initialization(api_client):
    assert api_client.api_url == "http://test.api"
    assert api_client.token == "test_token"
    assert api_client._queue == []

@pytest.mark.asyncio
async def test_send_batch(api_client):
    data = [{"id": 1}, {"id": 2}]
    
    # 由于目前 send_batch 只是打印日志，我们主要确保它能正常调用不报错
    # 未来这里可以 mock httpx/aiohttp 来验证请求发送
    await api_client.send_batch(data)
