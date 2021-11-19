import asyncio
import json
import logging
import time

import pytest
from websockets.legacy.server import WebSocketServer
import websockets
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import Value, on_connect, clearTriggerMessage, waitConnectorStatus, \
    waitServerClose, waitRequest


@pytest.mark.asyncio
async def test_remote_start_transaction_cable_plugged(event_loop):
    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
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
    flag = await waitRequest("authorize")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@pytest.mark.asyncio
async def test_remote_start_transaction(event_loop):
    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    Value.flag_boot_notification = 0
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
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
    flag = await waitRequest("authorize")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 获取结束充电后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


#timeout: 刷卡进入preparing,超时则进入available
@pytest.mark.skip(reason="需要刷卡")
@pytest.mark.asyncio
async def test_remote_start_transaction_time_out(event_loop):
    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"ConnectionTimeOut"
    Value.flag_boot_notification = 0
    response = await service.changeConfiguration(event_loop, key="ConnectionTimeOut", value="60")
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
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
    flag = await waitRequest("authorize")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    logging.info(time.time())
    status = await waitConnectorStatus(1, "Available", 20)
    assert status == "Available"
    logging.info(time.time())

    # 拔枪。。。待补充


@pytest.mark.asyncio
async def test_remote_stop_transaction(event_loop):
    flag = await waitRequest("boot_notification", 100)
    assert flag == True

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
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
    flag = await waitRequest("authorize")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"