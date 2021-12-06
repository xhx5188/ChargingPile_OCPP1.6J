import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
import allure


@allure.feature("test_remote_start_charging_session_rejected")
@pytest.mark.asyncio
async def test_remote_start_charging_session_rejected(event_loop):
    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="false")
    assert response[0].status == "Accepted"

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../test_2_08_resetting_happy_flow/schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待充电桩发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 再次发送充电请求
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.rejected


@allure.feature("test_remote_start_transaction_connector_id_shall_not_be_0")
@pytest.mark.asyncio
async def test_remote_start_transaction_connector_id_shall_not_be_0(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    with open("../test_2_08_resetting_happy_flow/schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=0,
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.rejected


@allure.feature("test_remote_stop_transaction_rejected")
@pytest.mark.asyncio
async def test_remote_stop_transaction_rejected(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../test_2_08_resetting_happy_flow/schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待充电桩发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 传输错误transactionId，结束远程充电失败
    response = await service.remoteStopTransaction(event_loop, 0)
    assert response[0].status == RegistrationStatus.rejected

    # 传输错误transactionId，结束远程充电失败
    response = await service.remoteStopTransaction(event_loop, 2)
    assert response[0].status == RegistrationStatus.rejected

    # 传输正确transactionId，结束远程充电成功
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"



