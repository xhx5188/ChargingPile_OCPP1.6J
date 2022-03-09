import asyncio
import logging
import pytest
import websockets
from websockets.legacy.server import WebSocketServer
from bluetooth.bluetooth import Buletooth
from connector.connector import Connector
from server import service
from server.connect import on_connect, waitServerClose, clearTriggerMessage, waitRequest, waitConnectorStatus, Value


@pytest.fixture(scope="function", autouse=True)
async def server(event_loop):
    await asyncio.sleep(10)
    clearTriggerMessage()
    logging.info("*" * 50 + "set up" + "*" * 50)
    Value.server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    flag, _ = await waitRequest("heartbeat", 200)
    if flag is True:
        logging.info("the charge point has connected to this server")
        logging.info("*" * 50 + "testcase" + "*" * 50)
        yield
        logging.info("*" * 50 + "tear down" + "*" * 50)
        status = await waitConnectorStatus(1, "Charging", 1)
        if status == "Charging":
            response = await service.remoteStopTransaction(event_loop, Value.transactionId)
            logging.info(response)
        Connector.unslot()

    else:
        logging.info("the charge point connect to this server timeout, and close server.")
    await waitServerClose(Value.server)
