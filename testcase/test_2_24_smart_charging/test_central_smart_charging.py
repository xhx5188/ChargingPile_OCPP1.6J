import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import waitRequest, clearTriggerMessage
import allure


@allure.feature("test_central_smart_charging")
@pytest.mark.asyncio
async def test_central_smart_charging(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    result = await service.setChargingProfile(event_loop, 1, )
    logging.info(result)

