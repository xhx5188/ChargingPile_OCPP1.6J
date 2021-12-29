import json
import logging
import time
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import Value, clearTriggerMessage, waitConnectorStatus, waitRequest
import allure


@allure.feature("test_remote_start_transaction_cable_plugged")
@pytest.mark.asyncio
async def test_remote_start_transaction_cable_plugged(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    assert flag == True
    logging.info(msg)
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction")
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearTriggerMessage()
    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪
    Connector.unslot()

    # 获取拔枪后的状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@allure.feature("test_remote_start_transaction")
@pytest.mark.asyncio
async def test_remote_start_transaction(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted

    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearTriggerMessage()
    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    # 获取结束充电后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪
    Connector.unslot()

    # 获取拔枪后的状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@allure.feature("test_remote_start_transaction_time_out")
@pytest.mark.asyncio
async def test_remote_start_transaction_time_out(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"ConnectionTimeOut"
    Value.flag_boot_notification = 0
    response = await service.changeConfiguration(event_loop, key="ConnectionTimeOut", value="60")
    assert response[0].status == RegistrationStatus.accepted

    # 远程启动充电
    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    logging.info(time.time())
    status = await waitConnectorStatus(1, "Available", 40)
    assert status == "Available"
    logging.info(time.time())


@allure.feature("test_remote_stop_transaction")
@pytest.mark.asyncio
async def test_remote_stop_transaction(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted

    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
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

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"
