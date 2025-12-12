import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from monitor.bilibili import BilibiliMonitor

# 真实的 API 响应样本
MOCK_LIVE_RESPONSE = {
    "code": 0,
    "msg": "ok",
    "data": {
        "room_id": 25207936,
        "live_status": 1,
        "title": "赶集啦",
        "area_name": "美食",
        "online": 1072
    }
}

MOCK_OFFLINE_RESPONSE = {
    "code": 0,
    "msg": "ok",
    "data": {
        "room_id": 25207936,
        "live_status": 0,
        "title": "休息中",
        "area_name": "美食",
        "online": 0
    }
}

@pytest.mark.asyncio
async def test_bilibili_monitor_initialization():
    monitor = BilibiliMonitor()
    assert monitor is not None

@pytest.mark.asyncio
async def test_check_status_live():
    monitor = BilibiliMonitor()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_LIVE_RESPONSE
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        is_live = await monitor.check_status("25207936")
        assert is_live is True

@pytest.mark.asyncio
async def test_check_status_offline():
    monitor = BilibiliMonitor()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_OFFLINE_RESPONSE
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        is_live = await monitor.check_status("25207936")
        assert is_live is False

@pytest.mark.asyncio
async def test_get_room_info_parsing():
    monitor = BilibiliMonitor()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_LIVE_RESPONSE
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        info = await monitor.get_room_info("25207936")
        
        assert info["room_id"] == "25207936"
        assert info["title"] == "赶集啦"
        assert info["live_status"] is True
        assert info["platform"] == "bilibili"
        assert info["online"] == 1072

@pytest.mark.asyncio
async def test_api_error_handling():
    monitor = BilibiliMonitor()
    
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Network Error")

    with patch("httpx.AsyncClient", return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        is_live = await monitor.check_status("25207936")
        assert is_live is False
        
        info = await monitor.get_room_info("25207936")
        assert info == {}

@pytest.mark.asyncio
async def test_real_api_call():
    """
    真实环境集成测试：直接请求 B 站 API
    注意：此测试依赖网络连接
    """
    monitor = BilibiliMonitor()
    # 使用 B 站官方直播间测试
    room_id = "7734200" 
    
    # 1. 测试 check_status
    # 我们不通过 assert True/False 来验证，因为无法保证它此刻的状态
    # 我们只验证它没有抛出异常，且返回了布尔值
    is_live = await monitor.check_status(room_id)
    assert isinstance(is_live, bool)
    
    # 2. 测试 get_room_info
    info = await monitor.get_room_info(room_id)
    
    # 验证返回的数据结构
    assert isinstance(info, dict)
    if info: 
        assert info["platform"] == "bilibili"
        # 注意：API 返回的 room_id 可能是 int 也可能是 str，我们代码里转成了 str
        assert str(info["room_id"]) == room_id
        assert "title" in info
        assert "live_status" in info
        assert isinstance(info["live_status"], bool)
