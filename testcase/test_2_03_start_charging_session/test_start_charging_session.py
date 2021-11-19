import pytest
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import Value, waitConnectorStatus, waitRequest


@pytest.mark.skip(reason = "需要本地开始充电")
@pytest.mark.asyncio
async def test_regular_charging_plugin_first(event_loop):
    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    # 改变配置信息"MeterValueSampleInterval"
    Value.flag_boot_notification = 0
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted

    await waitConnectorStatus(0, "Preparing")

