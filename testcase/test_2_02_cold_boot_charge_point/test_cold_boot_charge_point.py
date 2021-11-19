from datetime import datetime

import pytest
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
from testcase.test_2_02_cold_boot_charge_point.conftest import Val


@pytest.mark.asyncio
async def test_cold_boot_charge_point(event_loop):
    Val.boot_reject_count = 0
    Val.boot_response_status = RegistrationStatus.rejected
    Val.last_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.interval = ""

    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    #拒绝客户端的bootnotification请求三次
    assert Val.boot_reject_count == 3

    #等待桩可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"

    #等待枪1可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.asyncio
async def test_cold_boot_charge_point_pending(event_loop):
    Val.boot_reject_count = 0
    Val.boot_response_status = RegistrationStatus.rejected
    Val.last_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.interval = ""

    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    # 拒绝客户端的bootnotification请求三次
    assert Val.boot_reject_count == 3

    # 改变配置信息"MeterValueSampleInterval"
    clearTriggerMessage()
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="5")
    assert response[0].status == RegistrationStatus.accepted

    #等待客户端发送bootnotification
    flag = await waitRequest("boot_notification")
    assert flag == True

    # 等待桩可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"

    # 等待枪1可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 获取配置信息"MeterValueSampleInterval"
    result = await service.getConfiguration(event_loop, ["MeterValueSampleInterval"])
    assert result[0]['value'] == "5"

