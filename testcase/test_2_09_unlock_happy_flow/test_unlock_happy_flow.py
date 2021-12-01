import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
import allure


@pytest.mark.skip(reason="no fixed cable")
@pytest.mark.asyncio
@allure.feature("test_unlock_connector_no_charging_no_fixed_cable")
async def test_unlock_connector_no_charging_no_fixed_cable(event_loop):
    #未插枪。。。

    #判断未插枪状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    #解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "Unlocked"


@pytest.mark.asyncio
@allure.feature("test_unlock_connector_no_charging_with_fixed_cable")
async def test_unlock_connector_no_charging_with_fixed_cable(event_loop):
    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    #为支撑sevadis平台，暂时修改为"UnlockFailed"状态
    assert response[0].status == "UnlockFailed"


# @pytest.mark.skip(reason="no fixed cable")
@pytest.mark.asyncio
@allure.feature("test_unlock_connector_with_charging_no_fixed_cable")
async def test_unlock_connector_with_charging_no_fixed_cable(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("./schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待本地发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 判断充电状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "Unlocked"

    # 等待本地发送结束充电请求
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪
    Connector.unslot()

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.asyncio
@allure.feature("test_unlock_connector_with_charging_with_fixed_cable")
async def test_unlock_connector_with_charging_with_fixed_cable(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("./schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待本地发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    # 为支撑sevadis平台，暂时修改为"Unlocked"状态
    assert response[0].status == "Unlocked"

    #结束充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送结束请求
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    #拔枪
    Connector.unslot()

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"