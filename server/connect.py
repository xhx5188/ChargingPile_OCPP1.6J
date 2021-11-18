import asyncio
import gc
import json
import logging
import time
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from websockets.legacy.server import WebSocketServer


class Value():
    bootnotification: int = 0
    chargePoint = None
    # connector = ["" for x in range(10)]
    connectorTotal = 10

    message_boot_notification = None
    message_firmware_status_notification = ""
    message_heartbeat = None
    message_meter_values = None
    message_status_notification = [{} for x in range(10)]

class ChargePoint(cp):
    @on(Action.Authorize)
    def on_authorize(self, **kwargs):
        return call_result.AuthorizePayload(
            id_tag_info={
                "status": "Accepted"
            }
        )

    @on(Action.BootNotification)
    def on_boot_notification(self, **kwargs):
        Value.bootnotification = 1
        Value.message_boot_notification = kwargs

        return call_result.BootNotificationPayload(
            # current_time="2021-03-13T07:07:01.557Z",
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on(Action.DataTransfer)
    def on_data_transfer(self, **kwargs):
        return call_result.DataTransferPayload(status="Accepted")

    @on(Action.DiagnosticsStatusNotification)
    def on_diagnostics_status_notification(self, **kwargs):
        return call_result.DiagnosticsStatusNotificationPayload()

    @on(Action.FirmwareStatusNotification)
    def on_firmware_status_notification(self, **kwargs):
        Value.message_firmware_status_notification = kwargs["status"]
        return call_result.FirmwareStatusNotificationPayload()

    @on(Action.Heartbeat)
    def on_heartbeat(self, **kwargs):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
            # current_time="2021-03-13T07:07:01.557Z"
        )

    @on(Action.MeterValues)
    def on_meter_values(self, **kwargs):
        logging.info(kwargs)
        Value.message_meter_values = kwargs
        return call_result.MeterValuesPayload()

    @on(Action.StatusNotification)
    def on_status_notification(self, **kwargs):
        connectorID = kwargs['connector_id']
        Value.message_status_notification[connectorID] = kwargs
        return call_result.StatusNotificationPayload()

    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id: int, id_tag: str, **kwargs):
        eg = {
            "status": RegistrationStatus.accepted
        }
        return call_result.StartTransactionPayload(
            transaction_id=connector_id,
            id_tag_info=eg
        )

    @on(Action.StopTransaction)
    def on_stop_transaction(self, **kwargs):
        dict = {
            "status": "Accepted"
        }
        return call_result.StopTransactionPayload(
            id_tag_info=dict
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


async def waitConnectorStatus(ConnectorID: int, expected_status: str, timeout: int = 6) ->str:
    count = 0
    while Value.message_status_notification[ConnectorID].get("status") != expected_status:
        await asyncio.sleep(10)
        count += 1

        if timeout == count:
            return Value.message_status_notification[ConnectorID].get("status")
    return Value.message_status_notification[ConnectorID].get("status")


async def waitFirmwareStatus(expected_status: str, timeout: int = 30) ->str:
    count = 0
    while Value.message_firmware_status_notification != expected_status.lower():
        await asyncio.sleep(10)
        count += 1

        if timeout == count:
            return Value.message_firmware_status_notification
    return Value.message_firmware_status_notification


def clearTriggerMessage():
    Value.message_boot_notification = None
    Value.message_firmware_status_notification = ""
    Value.message_heartbeat = None
    Value.message_meter_values = None
    Value.message_status_notification = [{} for x in range(10)]


async def waitServerClose(server: WebSocketServer):
    server.close()
    gc.collect()
    await asyncio.sleep(40)
