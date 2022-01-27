import asyncio
import logging
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from websockets.legacy.server import WebSocketServer


class Value():
    server: WebSocketServer = None
    chargePoint = None
    transactionId_1 = 1
    transactionId_2 = 2
    connectorTotal = 10
    flag = {"authorize": [], "boot_notification": [], "data_transfer": [],
            "diagnostics_status_notification": [], "firmware_status_notification": [],
            "heartbeat": [], "meter_values": [], "status_notification": [],
            "start_transaction": [], "stop_transaction": [], "extended_trigger_message": [],
            "sign_certificate": []}

    message_boot_notification = None
    message_heartbeat = None
    message_meter_values = None
    message_status_notification = [{} for x in range(10)]


def clearTriggerMessage():
    Value.transactionId_1 = 1
    Value.transactionId_2 = 2
    Value.message_boot_notification = None
    Value.message_heartbeat = None
    Value.message_meter_values = None
    Value.message_status_notification = [{} for x in range(10)]

    for k, _ in Value.flag.items():
        Value.flag[k] = []

# tmp = 1

class ChargePoint(cp):
    @on(Action.Authorize)
    def on_authorize(self, **kwargs):
        Value.flag["authorize"].append(kwargs)
        return call_result.AuthorizePayload(
            id_tag_info={
                "status": "Accepted"
            }
        )

    @on(Action.BootNotification)
    def on_boot_notification(self, **kwargs):
        Value.flag["boot_notification"].append(kwargs)
        Value.message_boot_notification = kwargs
        # global tmp
        # if tmp == 1:
        #     tmp += 1
        #     return call_result.BootNotificationPayload(
        #         current_time="2048-00-00T00:00:00.000Z",
        #         # current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
        #         interval=10,
        #         status=RegistrationStatus.accepted
        #     )


        return call_result.BootNotificationPayload(
            # current_time="2021-03-13T07:07:01.557Z",
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on(Action.DataTransfer)
    def on_data_transfer(self, **kwargs):
        Value.flag["data_transfer"].append(kwargs)
        return call_result.DataTransferPayload(status="Accepted")

    @on(Action.DiagnosticsStatusNotification)
    def on_diagnostics_status_notification(self, **kwargs):
        Value.flag["diagnostics_status_notification"].append(kwargs)
        return call_result.DiagnosticsStatusNotificationPayload()

    @on(Action.FirmwareStatusNotification)
    def on_firmware_status_notification(self, **kwargs):
        Value.flag["firmware_status_notification"].append(kwargs)
        Value.flag["firmware_status_notification"][-1]["timestamp"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
        return call_result.FirmwareStatusNotificationPayload()

    @on(Action.Heartbeat)
    def on_heartbeat(self, **kwargs):
        Value.flag["heartbeat"].append({"timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')})
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z')
            # current_time="2021-03-13T07:07:01.557Z"
        )

    @on(Action.MeterValues)
    def on_meter_values(self, **kwargs):
        Value.flag["meter_values"].append(kwargs)
        Value.message_meter_values = kwargs
        return call_result.MeterValuesPayload()

    @on(Action.StatusNotification)
    def on_status_notification(self, **kwargs):
        Value.flag["status_notification"].append(kwargs)
        connectorID = kwargs['connector_id']
        Value.message_status_notification[connectorID] = kwargs
        return call_result.StatusNotificationPayload()

    @on(Action.StartTransaction)
    def on_start_transaction(self, **kwargs):
        Value.flag["start_transaction"].append(kwargs)
        eg = {
            "status": RegistrationStatus.accepted
        }
        if kwargs["connectorId"] == 1:
            return call_result.StartTransactionPayload(
                transaction_id = Value.transactionId_1,
                id_tag_info = eg
            )
        elif kwargs["connectorId"] == 2:
            return call_result.StartTransactionPayload(
                transaction_id=Value.transactionId_2,
                id_tag_info=eg
            )

    @on(Action.StopTransaction)
    def on_stop_transaction(self, **kwargs):
        Value.flag["stop_transaction"].append(kwargs)
        dict = {
            "status": "Accepted"
        }
        return call_result.StopTransactionPayload(
            id_tag_info = dict
        )

    @on(Action.SignCertificate)
    def on_sign_certificate(self, **kwargs):
        Value.flag["sign_certificate"].append(kwargs)
        return call_result.SignCertificatePayload(
            status="Accepted"
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


async def waitConnectorStatus(ConnectorID: int, expected_status: str, timeout: int = 10) ->str:
    count = 0
    while Value.message_status_notification[ConnectorID].get("status") != expected_status:
        await asyncio.sleep(3)
        count += 1

        if timeout == count:
            return Value.message_status_notification[ConnectorID].get("status")

    result = Value.message_status_notification[ConnectorID]["status"]
    Value.message_status_notification[ConnectorID]["status"] = None
    return result

async def waitRequest(requestType:str = "", timeout: int = 10):
    count = 0
    while not Value.flag.get(requestType):
        await asyncio.sleep(3)
        if timeout == count:
            return False, Value.flag.get(requestType)
        count += 1
    msg = Value.flag.get(requestType)[0]
    # 清空已处理的请求的内容，等待下一个请求
    del (Value.flag.get(requestType)[0])
    return True, msg


async def waitServerClose(server: WebSocketServer):
    server.close()
    # gc.collect()
    await asyncio.sleep(12)
