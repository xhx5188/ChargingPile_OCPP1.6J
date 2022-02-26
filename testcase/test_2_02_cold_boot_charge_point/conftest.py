import asyncio
from connector.connector import Connector
from server import service
from server.connect import waitServerClose, waitConnectorStatus
import logging
from datetime import datetime
import pytest
from ocpp.v16.enums import RegistrationStatus
from server.connect import Value, clearTriggerMessage, ChargePoint
from ocpp.routing import on
from ocpp.v16.enums import Action
from ocpp.v16 import call_result

@pytest.fixture(scope="function", autouse=True)
async def server(event_loop):
    await asyncio.sleep(10)
    clearTriggerMessage()
    logging.info("*" * 50 + "set up" + "*" * 50)
    logging.info("*" * 50 + "testcase" + "*" * 50)
    yield
    logging.info("*" * 50 + "tear down" + "*" * 50)
    status = await waitConnectorStatus(1, "Charging", 1)
    if status == "Charging":
        response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
        logging.info(response)
    Connector.unslot()
    await waitServerClose(Value.server)


@pytest.fixture(scope="function", autouse=True)
async def reboot(event_loop):
    logging.info("掉电")
    Connector.unelectricity()
    await asyncio.sleep(60)
    logging.info("上电")
    Connector.electricity()
    yield


class Val:
    boot_reject_count = 0
    last_time = ""
    current_time = ""
    interval = 7
    flag_pend = True


class ChargePointReject(ChargePoint):
    @on(Action.BootNotification)
    def on_boot_notification(self, **kwargs):
        if Val.boot_reject_count < 3:
            Val.boot_reject_count += 1
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
                interval=3,
                status=RegistrationStatus.rejected
            )
        else:
            Value.flag["boot_notification"].append(kwargs)
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
                interval=Val.interval,
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


class ChargePointPending(ChargePoint):
    @on(Action.BootNotification)
    def on_boot_notification(self, **kwargs):
        Value.flag["boot_notification"].append(kwargs)
        if Val.flag_pend == True:
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
                interval=3,
                status=RegistrationStatus.pending
            )
        else:
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'),
                interval=Val.interval,
                status=RegistrationStatus.accepted
            )


async def on_connect_boot_pending(websocket, path):
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
    Value.chargePoint = ChargePointPending(charge_point_id, websocket)
    await Value.chargePoint.start()