import asyncio
import json
import logging
from datetime import datetime, timedelta

import pytest
from websockets.legacy.server import WebSocketServer
import websockets

from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ResetType

from server import service
from server.connect import Value, on_connect, clearTriggerMessage, waitConnectorStatus, waitFirmwareStatus


def setup_function():
    logging.info("testcase started")


def teardown_function():
    Value.bootnotification = 0
    logging.info("testcase finished")


@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value=0)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"MeterValueSampleInterval"
    response = await service.getConfiguration(event_loop)
    configs = response[0].configuration_key
    result = [i["value"] for i in configs if i["key"] == "MeterValueSampleInterval" and i['readonly'] != True]
    assert result[0] == 0

    # 改变配置信息"ClockAlignedDataInterval"
    response = await service.changeConfiguration(event_loop, key="ClockAlignedDataInterval", value=0)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"ClockAlignedDataInterval"
    response = await service.getConfiguration(event_loop)
    configs = response[0].configuration_key
    result = [i["value"] for i in configs if i["key"] == "ClockAlignedDataInterval" and i['readonly'] != True]
    assert result[0] == 0

    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="false")
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"LocalPreAuthorize"
    response = await service.getConfiguration(event_loop)
    configs = response[0].configuration_key
    result = [i["value"] for i in configs if i["key"] == "LocalPreAuthorize" and i['readonly'] != True]
    assert result[0] == "false"