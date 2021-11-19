import logging

import pytest
import websockets
from websockets.legacy.server import WebSocketServer

from server.connect import on_connect, waitServerClose, clearTriggerMessage

logging.basicConfig(level=logging.INFO)

@pytest.fixture(scope="function", autouse=True)
async def server():
    clearTriggerMessage()
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    yield server
    await waitServerClose(server)