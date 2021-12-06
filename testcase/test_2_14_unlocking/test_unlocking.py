import pytest
from server import service
import allure


@allure.feature("test_unlock_failure")
@pytest.mark.asyncio
async def test_unlock_failure(event_loop):
    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "UnlockFailed"


@allure.feature("test_unknown_connector")
@pytest.mark.asyncio
async def test_unknown_connector(event_loop):
    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=2)
    assert response[0].status == "NotSupported"