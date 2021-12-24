import asyncio
import websockets
from websockets.legacy.server import WebSocketServer
from connector.connector import Connector
from server import service
from server.connect import waitServerClose, waitConnectorStatus, waitRequest
import logging
import pytest
from server.connect import Value, clearTriggerMessage, ChargePoint
from ocpp.routing import on
from ocpp.v16.enums import Action
from ocpp.v16 import call_result

@pytest.fixture(scope="function", autouse=True)
async def server(event_loop):
    await asyncio.sleep(10)
    clearTriggerMessage()
    logging.info("*" * 50 + "set up" + "*" * 50)
    Value.server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    flag, _ = await waitRequest("heartbeat")
    if flag == True:
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



class ChargePointRejectAuthorize(ChargePoint):
    @on(Action.Authorize)
    def on_authorize(self, **kwargs):
        Value.flag["authorize"].append(kwargs)
        return call_result.AuthorizePayload(
            id_tag_info={
                "status": "Invalid"
            }
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
    Value.chargePoint = ChargePointRejectAuthorize(charge_point_id, websocket)
    await Value.chargePoint.start()
