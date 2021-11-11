import asyncio
import json
import logging
import time
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp, call
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)

class Value():
    bootnotification: int = 0
    chargePoint = None
    connector = ["" for x in range(0, 10)]
    connectorTotal = 10

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

    @on(Action.StatusNotification)
    def on_status_notification(self, **kwargs):
        connectorID = kwargs['connector_id']
        Value.connector[connectorID] = kwargs['status']
        return call_result.StatusNotificationPayload()

    @on(Action.Authorize)
    def on_authorize(self, **kwargs):
        return call_result.AuthorizePayload(
            id_tag_info = {
                "status": "Accepted"
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
    Value.chargePoint = ChargePoint(charge_point_id, websocket)
    await Value.chargePoint.start()

def waitConnectorStatus(ConnectorID: int, timeout: int = 6) ->str:
    count = 0
    while not Value.connector[ConnectorID]:
        time.sleep(1)
        count += 1

        if timeout == count:
            return ""
    return Value.connector[ConnectorID]

