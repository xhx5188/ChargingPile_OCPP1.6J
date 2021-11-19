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
    clearTriggerMessage()


def teardown_function():
    Value.bootnotification = 0
    logging.info("testcase finished")


@pytest.mark.skip(reason = "需要本地开始充电")
@pytest.mark.asyncio
async def test_regular_charging_plugin_first(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # 改变配置信息"MeterValueSampleInterval"
    Value.bootnotification = 0
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted

    await waitConnectorStatus(0, "Preparing")



    await waitServerClose(server)