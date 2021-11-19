import asyncio
import logging
import time
from datetime import datetime

import pytest
from websockets.legacy.server import WebSocketServer
import websockets
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import Value, on_connect, clearTriggerMessage, waitConnectorStatus, waitFirmwareStatus, \
    waitServerClose, ChargePoint
from ocpp.routing import on
from ocpp.v16.enums import Action
from ocpp.v16 import call_result


def setup_function():
    logging.info("testcase started")
    clearTriggerMessage()


def teardown_function():
    Value.bootnotification = 0
    logging.info("testcase finished")


@pytest.mark.asyncio
async def test_cold_boot_charge_point(event_loop):
    Val.boot_reject_count = 0
    Val.boot_response_status = RegistrationStatus.rejected
    Val.last_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.interval = ""

    server: WebSocketServer = await websockets.serve(on_connect_boot_reject, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    #拒绝客户端的bootnotification请求三次
    assert Val.boot_reject_count == 3

    #等待桩可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"

    #等待枪1可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_cold_boot_charge_point_pending(event_loop):
    Val.boot_reject_count = 0
    Val.boot_response_status = RegistrationStatus.rejected
    Val.last_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
    Val.interval = ""

    server: WebSocketServer = await websockets.serve(on_connect_boot_reject, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # 拒绝客户端的bootnotification请求三次
    assert Val.boot_reject_count == 3

    # 改变配置信息"MeterValueSampleInterval"
    Value.bootnotification = 0
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="5")
    assert response[0].status == RegistrationStatus.accepted

    #等待客户端发送bootnotification
    times = 0
    while Value.bootnotification == 0:
        logging.info(Value.bootnotification)
        await asyncio.sleep(3)
        times += 1
        if times >= 10:
            assert 0 == 1
    assert Value.bootnotification == 1

    # 等待桩可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"

    # 等待枪1可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 获取配置信息"MeterValueSampleInterval"
    result = await service.getConfiguration(event_loop, "MeterValueSampleInterval")
    assert result[0] == "5"

    await waitServerClose(server)


class ChargePointReject(ChargePoint):
    @on(Action.BootNotification)
    def on_boot_notification(self, **kwargs):
        from dateutil.parser import parse
        Val.current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
        a = parse(Val.current_time)
        b = parse(Val.last_time)
        if Val.current_time != 0:
            Val.interval = (a - b).seconds
            logging.info("the value of interval is:%s" % Val.interval)
        Val.current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
        Val.last_time = Val.current_time

        if Val.boot_reject_count < 3:
            Val.boot_reject_count += 1
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
                interval=3,
                status=Val.boot_response_status
            )
        else:
            Value.bootnotification = 1
            Value.message_boot_notification = kwargs
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
                interval=3,
                status=RegistrationStatus.accepted
            )


async def on_connect_boot_reject(websocket, path):
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.error(
            "Client hasn't requested any Subprotocol. Closing Connection"
        )
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    Value.chargePoint = ChargePointReject(charge_point_id, websocket)
    await Value.chargePoint.start()

class Val:
    boot_reject_count = 0,
    last_time = "",
    current_time = "",
    interval = ""
    boot_response_status = ""

