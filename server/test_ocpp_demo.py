import asyncio
import json
from time import sleep

import pytest
from websockets.legacy.server import WebSocketServer
import websockets

from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ResetType
from server.conftest import Value, on_connect, waitConnectorStatus


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
        await asyncio.sleep(1)

    Value.connector[0] = ""
    request = call.RemoteStartTransactionPayload(id_tag='AE0022A1GM9C00041C', connector_id=1)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    # assert response[0].status == RegistrationStatus.accepted

    # status = waitConnectorStatus(0)
    # for i in Value.connector:
    #     print(i)
    # assert status == "Available"
    sleep(300)
    server.close()


@pytest.mark.asyncio
async def test_remote_start_and_stop_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/remote_start_transaction/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    request = call.RemoteStartTransactionPayload(id_tag=data['idTag'], connector_id=data['connectorId'], charging_profile=data['chargingProfile'])
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    request = call.RemoteStopTransactionPayload(transaction_id=data['chargingProfile']['transactionId'])
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_reset_hard(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request=call.ResetPayload(type=ResetType.hard)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


