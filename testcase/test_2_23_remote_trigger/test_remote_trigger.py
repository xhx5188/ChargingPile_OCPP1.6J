import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import waitRequest, clearTriggerMessage
import allure


@allure.feature("test_trigger_message")
@pytest.mark.asyncio
async def test_trigger_message(event_loop):
    response = await service.triggerMessage(event_loop, requested_message="MeterValues")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送测量数据
    flag, _ = await waitRequest("meter_values")
    assert flag == True

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="Heartbeat")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送心跳
    flag, _ = await waitRequest("heartbeat")
    assert flag == True

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="StatusNotification")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送状态通知
    flag, _ = await waitRequest("status_notification")
    assert flag == True

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="DiagnosticsStatusNotification")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送诊断状态通知
    flag, _ = await waitRequest("diagnostics_status_notification")
    assert flag == True

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="FirmwareStatusNotification")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送固件状态信息
    flag, _ = await waitRequest("firmware_status_notification")
    assert flag == True

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="BootNotification")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地boot通知
    flag, _ = await waitRequest("boot_notification")
    assert flag == True


@allure.feature("test_trigger_rejected")
@pytest.mark.asyncio
async def test_trigger_rejected(event_loop):
    response = await service.triggerMessage(event_loop, requested_message="MeterValues", connector_id=2)
    assert response[0].status == RegistrationStatus.rejected
