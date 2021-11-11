import asyncio
import logging
from datetime import datetime
from time import sleep
from ocpp.routing import on
from ocpp.v16.enums import Action
from ocpp.v16 import call_result

try:
    import websockets
except ModuleNotFoundError:
    logging.info("This example relies on the 'websockets' package.")
    logging.info("Please install it by running: ")
    logging.info()
    logging.info(" $ pip install websockets")
    import sys
    sys.exit(1)


from ocpp.v16 import call
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(Action.RemoteStartTransaction)
    def on_remote_start_transaction(self, **kwargs):
        return call_result.RemoteStartTransactionPayload(
            status=RegistrationStatus.accepted
        )

    @on(Action.RemoteStopTransaction)
    def on_remote_stop_transaction(self, **kwargs):
        return call_result.RemoteStopTransactionPayload(
            status=RegistrationStatus.accepted
        )

    @on(Action.Reset)
    def on_Reset(self, **kwargs):
        return call_result.ResetPayload(
            status=RegistrationStatus.accepted
        )

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )

        response = await self.call(request)
        if response.status == RegistrationStatus.accepted:
            logging.info("send_boot_notification success.")
        return response

    async def send_start_transaction(self):
        request = call.StartTransactionPayload(
            connector_id=1,
            id_tag='AE0022A1GM9C00041C',
            meter_start=1,
            timestamp=datetime.utcnow().isoformat()
        )

        response = await self.call(request)
        if response.id_tag_info['status'] == RegistrationStatus.accepted:
            logging.info("send_start_transaction success.")
        return response

    async def send_status_notification(self, connector_id, status, error_code):
        request = call.StatusNotificationPayload(
            connector_id=connector_id,
            status=status,
            error_code=error_code
        )
        response = await self.call(request)
        return response

    async def send_authorize(self):
        request = call.AuthorizePayload(
            id_tag='AE0022A1GM9C00041C'
        )
        response = await self.call(request)
        return response




async def main():
    async with websockets.connect(
        'ws://192.168.31.186:9000/CP_1',
        subprotocols=['ocpp1.6']
    ) as ws:

        cp = ChargePoint('CP_1', ws)

        responce = await asyncio.gather(cp.get_a_start(), cp.send_boot_notification())
        assert responce[1].status == 'Accepted'

        logging.info('*' * 100)

        tasks = [cp.get_a_start(), cp.send_start_transaction()]
        await asyncio.wait(tasks)
        logging.info('*' * 100)

        # sleep(15)
        tasks = [cp.get_a_start(), cp.send_status_notification(0, "Available", "NoError")]
        await asyncio.wait(tasks)
        logging.info('*' * 100)

        tasks = [cp.get_a_start(), cp.send_status_notification(0, "Preparing", "NoError")]
        await asyncio.wait(tasks)
        logging.info('*' * 100)

        tasks = [cp.get_a_start(), cp.send_authorize()]
        await asyncio.wait(tasks)
        logging.info('*' * 100)

        tasks = [cp.start()]
        await asyncio.wait(tasks)
        logging.info('*' * 100)

        while True:
            pass

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





