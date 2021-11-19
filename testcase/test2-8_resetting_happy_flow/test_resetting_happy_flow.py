import asyncio
import json
import logging
import time

import pytest
from websockets.legacy.server import WebSocketServer
import websockets
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import Value, on_connect, clearTriggerMessage, waitConnectorStatus, waitFirmwareStatus, \
    waitServerClose, waitAuthorize


def setup_function():
    logging.info("testcase started")
    clearTriggerMessage()


def teardown_function():
    Value.bootnotification = 0
    logging.info("testcase finished")


@pytest.mark.asyncio
async def test_hard_reset_without_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    #等待桩状态为可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    #远程设置桩为不可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    #重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Hard")
    assert response[0].status == RegistrationStatus.accepted

    #等待充电桩重启
    server.close()
    Value.bootnotification = 0
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)
    assert Value.bootnotification == 1

    #判断重启之后桩的状态任不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 远程设置桩为可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_soft_reset_without_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    #等待桩状态为可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    #远程设置桩为不可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    #重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Soft")
    assert response[0].status == RegistrationStatus.accepted

    #等待充电桩重启
    server.close()
    Value.bootnotification = 0
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)
    assert Value.bootnotification == 1

    #判断重启之后桩的状态任不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 远程设置桩为可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_hard_reset_with_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, "AuthorizeRemoteTxRequests")
    logging.info(result)
    assert result[0] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    Value.bootnotification = 0
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="15")
    assert response[0].status == RegistrationStatus.accepted

    #等待桩状态为可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
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
    flag = await waitAuthorize()
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    #重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Hard")
    assert response[0].status == RegistrationStatus.accepted

    #等待充电桩重启
    assert Value.bootnotification == 1





    # 等待桩状态为可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    await waitServerClose(server)