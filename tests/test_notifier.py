import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from utils.notifier import AudioServiceNotifier

@pytest.mark.asyncio
async def test_notify_success():
    # Setup
    url = "http://audio-service/api/webhook"
    notifier = AudioServiceNotifier(url)
    
    # Mock httpx client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    
    notifier.client.post = AsyncMock(return_value=mock_response)
    
    # Execute
    result = await notifier.notify("123", "start")
    
    # Verify
    assert result is True
    notifier.client.post.assert_called_once_with(
        url, 
        json={"room_id": "123", "action": "start", "platform": "bilibili"}
    )
    
    await notifier.close()

@pytest.mark.asyncio
async def test_notify_no_url():
    # Setup with None URL
    notifier = AudioServiceNotifier(None)
    notifier.client.post = AsyncMock()
    
    # Execute
    result = await notifier.notify("123", "start")
    
    # Verify
    assert result is True
    notifier.client.post.assert_not_called()
    
    await notifier.close()

@pytest.mark.asyncio
async def test_notify_failure():
    # Setup
    url = "http://audio-service/api/webhook"
    notifier = AudioServiceNotifier(url)
    
    # Mock httpx client to raise error
    import httpx
    notifier.client.post = AsyncMock(side_effect=httpx.HTTPError("Network error"))
    
    # Execute
    result = await notifier.notify("123", "start")
    
    # Verify
    assert result is False
    
    await notifier.close()
