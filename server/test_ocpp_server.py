import asyncio
import json
import logging
import time
from datetime import datetime
from time import sleep

import pytest
from websockets.legacy.server import WebSocketServer

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp, call
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)

class Value():
    bootnotification = 0

class ChargePoint(cp):
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        Value.bootnotification = 1
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id: int, id_tag: str, **kwargs):
        eg = {
            # "expiryDate": datetime.utcnow().isoformat(),
            # "parentIdTag": "111111",
            "status": RegistrationStatus.accepted
        }
        return call_result.StartTransactionPayload(
            transaction_id=connector_id,
            id_tag_info=eg
        )

async def on_connect(websocket, path):
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
    global cp
    cp = ChargePoint(charge_point_id, websocket)
    await cp.start()



def setup_function():
    print("testcase started")

def teardown_function():
    Value.bootnotification = 0
    print("testcase finished")

@pytest.mark.asyncio
async def test_remote_start_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(3)

    request=call.RemoteStartTransactionPayload(id_tag='AE0022A1GM9C00041C', connector_id=1)
    tasks = [event_loop.create_task(cp.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_remote_start_and_stop_transaction_(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(3)

    with open("./schema/remote_start_transaction/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    request = call.RemoteStartTransactionPayload(id_tag=data['idTag'], connector_id=data['connectorId'], charging_profile=data['chargingProfile'])
    tasks = [event_loop.create_task(cp.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    request = call.RemoteStopTransactionPayload(transaction_id=data['chargingProfile']['transactionId'])
    tasks = [event_loop.create_task(cp.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()














