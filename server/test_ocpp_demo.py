import asyncio
import json
import logging
from datetime import datetime, timedelta
from time import sleep

import pytest
from websockets.legacy.server import WebSocketServer
import websockets

from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ResetType
from server.connect import Value, on_connect, waitConnectorStatus, clearConnectorStatus, clearTriggerMessage


def setup_function():
    print("testcase started")


def teardown_function():
    Value.bootnotification = 0
    print("testcase finished")


@pytest.mark.asyncio
async def test_remote_start_and_stop_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/remote_start_transaction/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)

    clearConnectorStatus()
    request = call.RemoteStartTransactionPayload(id_tag=data.get('idTag'), connector_id=data.get('connectorId'),
                                                 charging_profile=data.get('chargingProfile'))
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearConnectorStatus()
    request = call.RemoteStopTransactionPayload(transaction_id=data['chargingProfile']['transactionId'])
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

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


#改变桩的可用性时桩不能处于preparing状态
@pytest.mark.asyncio
async def test_change_availability(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.ChangeAvailabilityPayload(connector_id=0, type="Inoperative")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    request = call.ChangeAvailabilityPayload(connector_id=0, type="Operative")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_clear_cache(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.ClearCachePayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_set_charging_profile(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/set_charge_profile/SetChargeProfile.json", 'r') as f:
        data = json.load(f)
    print(data)
    request = call.SetChargingProfilePayload(connector_id=0, cs_charging_profiles=data)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_clear_charge_profile(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/clear_charge_profile/ClearChargeProfile.json", 'r') as f:
        data = json.load(f)
    request = call.ClearChargingProfilePayload(id=data.get("id"), connector_id=data.get("connectorId"),
                                               charging_profile_purpose=data.get("chargingProfilePurpose"),
                                               stack_level=data.get("stackLevel"))
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_data_transfer(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.DataTransferPayload("AUTEL", "111", "data")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.rejected

    server.close()


@pytest.mark.asyncio
async def test_get_composite_schedule(event_loop):
    pass


@pytest.mark.asyncio
async def test_get_configuration(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.GetConfigurationPayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    print(response[0].configuration_key)

    server.close()


@pytest.mark.asyncio
async def test_get_diagnostics(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.GetDiagnosticsPayload('/diagnostics')
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    print(response)

    server.close()


@pytest.mark.asyncio
async def test_send_get_local_list(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # send local list to the charge point in case of full update
    with open("./schema/send_local_list/SendLocalList1.json", 'r') as f:
        data = json.load(f)
    request = call.SendLocalListPayload(list_version=data.get("listVersion"),
                                        update_type=data.get("updateType"),
                                        local_authorization_list=data.get("localAuthorizationList"))
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    # get local list for the charge point
    request = call.GetLocalListVersionPayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    # send local list to the charge point in case of full update
    with open("./schema/send_local_list/SendLocalList2.json", 'r') as f:
        data = json.load(f)
    request = call.SendLocalListPayload(list_version=data.get("listVersion"),
                                        update_type=data.get("updateType"),
                                        local_authorization_list=data.get("localAuthorizationList"))
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    # get local list for the charge point
    request = call.GetLocalListVersionPayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    # send local list to the charge point in case of full update
    with open("./schema/send_local_list/SendLocalList3.json", 'r') as f:
        data = json.load(f)
    request = call.SendLocalListPayload(list_version=data.get("listVersion"),
                                        update_type=data.get("updateType"),
                                        local_authorization_list=data.get("localAuthorizationList"))
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    # get local list for the charge point
    request = call.GetLocalListVersionPayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    server.close()


@pytest.mark.asyncio
async def test_get_reserve_now(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    expiry_date = (datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%dT%H:%M:%S.001Z')
    request = call.ReserveNowPayload(connector_id=1, expiry_date=expiry_date, id_tag="AE0022A1GM9C00041C", reservation_id=1)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    logging.info(response)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_reset_hard(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.ResetPayload(type="Hard")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    logging.info(response)
    assert response[0].status == RegistrationStatus.accepted
    server.close()
    Value.bootnotification = 0

    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    timeout = 0
    while Value.bootnotification == 0 and timeout <= 60:
        await asyncio.sleep(1)
        timeout += 1
    if timeout > 60:
        assert False

    server.close()


@pytest.mark.asyncio
async def test_reset(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.ResetPayload(type="Hard")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_reset_soft(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.ResetPayload(type="Soft")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_trigger_message_boot_notification(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    assert Value.message_boot_notification == None
    request = call.TriggerMessagePayload(requested_message="BootNotification")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(3)
    assert Value.message_boot_notification["charge_point_model"] == "MaxiChargerAC"
    assert Value.message_boot_notification["charge_point_vendor"] == "Autel"

    server.close()


@pytest.mark.asyncio
async def test_trigger_message_heartbeat(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.TriggerMessagePayload(requested_message="Heartbeat")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_trigger_message_meter_values(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    request = call.TriggerMessagePayload(requested_message="MeterValues")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(3)
    print(Value.message_meter_values)
    assert Value.message_meter_values["transaction_id"] == -1

    server.close()


@pytest.mark.asyncio
async def test_trigger_message_status_notification(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    request = call.TriggerMessagePayload(requested_message="MeterValues")
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(3)
    print(Value.message_status_notification)
    assert Value.message_status_notification[0]["status"] == "Available"
    assert Value.message_status_notification[0]["connector_id"] == 0
    assert Value.message_status_notification[1]["status"] == "Preparing"
    assert Value.message_status_notification[1]["connector_id"] == 1

    server.close()


@pytest.mark.asyncio
async def test_update_firmware(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    request = call.UpdateFirmwarePayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(3)
    print(Value.message_status_notification)
    assert Value.message_status_notification[0]["status"] == "Available"
    assert Value.message_status_notification[0]["connector_id"] == 0
    assert Value.message_status_notification[1]["status"] == "Preparing"
    assert Value.message_status_notification[1]["connector_id"] == 1

    server.close()


@pytest.mark.asyncio
async def test_unlock_connector(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    request = call.UnlockConnectorPayload(connector_id=1)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    assert response[0].status == "UnlockFailed"

    server.close()
