import asyncio
import json
import logging
from datetime import datetime
from time import sleep

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

bootnotification = 0
class ChargePoint(cp):
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        global bootnotification
        bootnotification = 1
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
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
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
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    global cp
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )

    logging.info("Server Started listening to new connections...")

    while bootnotification == 0:
        await asyncio.sleep(10)

    request = call.RemoteStartTransactionPayload(
        id_tag='AE0022A1GM9C00041C',
        connector_id=1
    )
    response = await cp.call(request)
    if response.status == RegistrationStatus.accepted:
        logging.info("remote_start_transaction success.")


    await server.wait_closed()




if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()