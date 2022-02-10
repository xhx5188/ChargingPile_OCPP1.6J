import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
import allure
from server.connect import waitConnectorStatus, clearTriggerMessage, waitRequest


@pytest.mark.skip(reason="需要socket版本的桩进行测试")
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


@pytest.mark.skip(reason="需要socket版本的桩进行测试")
@allure.feature("test_unlock_on_charging")
@pytest.mark.asyncio
async def test_unlock_on_charging(event_loop):
    # 插枪
    Connector.slot()

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    logging.info(response)
    assert response[0].status == "Unlocked"


    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg["reason"] == "UnlockCommand"