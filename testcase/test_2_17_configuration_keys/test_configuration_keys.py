import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure

@allure.feature("test_configuration_1")
@pytest.mark.asyncio
async def test_configuration_1(event_loop):
    # 改变配置信息"Testing"
    response = await service.changeConfiguration(event_loop, key="Testing", value="test")
    assert response[0].status == "NotSupported"


@allure.feature("test_configuration_2")
@pytest.mark.asyncio
async def test_configuration_2(event_loop):
    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="-1")
    assert response[0].status == RegistrationStatus.rejected