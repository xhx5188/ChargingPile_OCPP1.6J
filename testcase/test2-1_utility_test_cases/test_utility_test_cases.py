import asyncio
import logging

import pytest
from websockets.legacy.server import WebSocketServer
import websockets
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import Value, on_connect, clearTriggerMessage, waitConnectorStatus, waitFirmwareStatus, \
    waitServerClose


def setup_function():
    logging.info("testcase started")


def teardown_function():
    Value.bootnotification = 0
    logging.info("testcase finished")


@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state1(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # 改变配置信息"MeterValueSampleInterval"
    value = "1"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value=value)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"MeterValueSampleInterval"
    result = await service.getConfiguration(event_loop, "MeterValueSampleInterval")
    assert result[0] == value

    # 改变配置信息"ClockAlignedDataInterval"
    response = await service.changeConfiguration(event_loop, key="ClockAlignedDataInterval", value=value)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"ClockAlignedDataInterval"
    result = await service.getConfiguration(event_loop, "ClockAlignedDataInterval")
    assert result[0] == value

    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="false")
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"LocalPreAuthorize"
    result = await service.getConfiguration(event_loop, "LocalPreAuthorize")
    assert result[0] == "false"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state2(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    #设置桩可用
    clearTriggerMessage()
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    #获取桩状态
    status = await waitConnectorStatus(ConnectorID=0, expected_status="Available")
    assert status == "Available"

    # 获取配置信息"AuthorizationCacheEnabled"
    # result = await service.getConfiguration(event_loop, "AuthorizationCacheEnabled")
    # assert result[0] == "true"

    await waitServerClose(server)

@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state3(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    #清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"LocalAuthListEnabled"
    result = await service.getConfiguration(event_loop, "LocalAuthListEnabled")
    assert result[0] == "true"

    # 获取配置信息"MaxChargingProfilesInstalled"
    result = await service.getConfiguration(event_loop, "MaxChargingProfilesInstalled")
    logging.info(result[0])
    if result[0] != "0":
        #清除充电配置文件
        response = await service.clearChargeProfile(event_loop, connector_id=0)
        assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)
