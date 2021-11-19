import websockets
from websockets.legacy.server import WebSocketServer

from server.connect import waitServerClose

import logging
from datetime import datetime

import pytest
from ocpp.v16.enums import RegistrationStatus

from server.connect import Value, clearTriggerMessage, ChargePoint
from ocpp.routing import on
from ocpp.v16.enums import Action
from ocpp.v16 import call_result

@pytest.fixture(scope="function", autouse=True)
async def server():
    clearTriggerMessage()
    server: WebSocketServer = await websockets.serve(on_connect_boot_reject, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Special server Started listening to new connections...")
    yield server
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
            Value.flag["boot_notification"] = 1
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