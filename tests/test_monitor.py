import pytest
from monitor.bilibili import BilibiliMonitor

@pytest.mark.asyncio
async def test_bilibili_monitor_initialization():
    monitor = BilibiliMonitor()
    assert monitor is not None

@pytest.mark.asyncio
async def test_check_status_default():
    monitor = BilibiliMonitor()
    # 目前实现默认返回 False
    status = await monitor.check_status("123456")
    assert status is False

@pytest.mark.asyncio
async def test_get_room_info_structure():
    monitor = BilibiliMonitor()
    room_id = "123456"
    info = await monitor.get_room_info(room_id)
    
    assert isinstance(info, dict)
    assert info["room_id"] == room_id
    assert info["platform"] == "bilibili"
