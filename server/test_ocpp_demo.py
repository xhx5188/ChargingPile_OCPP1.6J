import asyncio
import json
import logging
import time
from datetime import datetime, timedelta

import pytest
from websockets.legacy.server import WebSocketServer
import websockets

from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ResetType

from server import service
from server.connect import Value, on_connect, clearTriggerMessage, waitConnectorStatus, waitFirmwareStatus, \
    waitServerClose


def setup_function():
    logging.info("testcase started")


def teardown_function():
    Value.bootnotification = 0
    logging.info("testcase finished")


@pytest.mark.asyncio
async def test_clear_cache1(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)



@pytest.mark.asyncio
async def test_clear_cache2(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_clear_cache3(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)

@pytest.mark.asyncio
async def test_remote_start_and_stop_transaction(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/remote_start_transaction/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'), connector_id=data.get('connectorId'),
                                                 charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    await waitServerClose(server)


#改变桩的可用性时桩不能处于preparing状态
@pytest.mark.skip(reason="charge point can not in preparing status")
@pytest.mark.asyncio
async def test_change_availability(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.changeAvailability(event_loop, connector_id=0, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_get_and_change_configuration(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    #改变配置信息
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="false")
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息
    result = await service.getConfiguration(event_loop, "LocalAuthListEnabled")
    assert result[0] == "false"

    # 改变配置信息
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息
    result = await service.getConfiguration(event_loop, "LocalAuthListEnabled")
    assert result[0] == "true"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_clear_cache(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.skip(reason="this interface is not supported")
@pytest.mark.asyncio
async def test_set_charging_profile(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/set_charge_profile/SetChargeProfile.json", 'r') as f:
        data = json.load(f)
    response = await service.setChargingProfile(event_loop, connector_id=0, cs_charging_profiles=data)
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_clear_charge_profile(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    with open("./schema/clear_charge_profile/ClearChargeProfile.json", 'r') as f:
        data = json.load(f)
    response = await service.clearChargeProfile(event_loop, id=data.get("id"), connector_id=data.get("connectorId"),
                                               charging_profile_purpose=data.get("chargingProfilePurpose"),
                                               stack_level=data.get("stackLevel"))
    assert response[0].status == "Unknown"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_data_transfer(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.dataTransfer(event_loop, "AUTEL", "111", "data")
    logging.info(response)
    assert response[0].status == RegistrationStatus.rejected

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_get_composite_schedule(event_loop):
    pass


#未调通
@pytest.mark.asyncio
async def test_get_diagnostics(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.getDiagnostics(event_loop, '/diagnostics')
    logging.info(response)

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_send_get_local_list(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    print("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    # send local list to the charge point in case of full update
    with open("./schema/send_local_list/SendLocalList1.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                        update_type=data.get("updateType"),
                                        local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # get local list for the charge point
    response = await service.getLocalList(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    # send local list to the charge point in case of full update
    with open("./schema/send_local_list/SendLocalList2.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # get local list for the charge point
    response = await service.getLocalList(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    # send local list to the charge point in case of full update
    with open("./schema/send_local_list/SendLocalList3.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # get local list for the charge point
    response = await service.getLocalList(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_reserve_now(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    expiry_date = (datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%dT%H:%M:%S.001Z')
    response = await service.reserveNow(event_loop, connector_id=1, expiry_date=expiry_date, id_tag="AE0022A1GM9C00041C", reservation_id=1)
    logging.info(response)
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_reset_hard(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.reset(event_loop, "Hard")
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
    assert Value.bootnotification == 1

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_reset(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.reset(event_loop, "Hard")
    assert response[0].status == RegistrationStatus.accepted

    server.close()


@pytest.mark.asyncio
async def test_reset_soft(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.reset(event_loop, "Soft")
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_trigger_message_boot_notification(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    assert Value.message_boot_notification == None
    response = await service.triggerMessage(event_loop, requested_message="BootNotification")
    assert response[0].status == RegistrationStatus.accepted

    await asyncio.sleep(3)
    assert Value.message_boot_notification["charge_point_model"] == "MaxiChargerAC"
    assert Value.message_boot_notification["charge_point_vendor"] == "Autel"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_trigger_message_heartbeat(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.triggerMessage(event_loop, requested_message="Heartbeat")
    assert response[0].status == RegistrationStatus.accepted

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_trigger_message_meter_values(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="MeterValues")
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(3)
    logging.info(Value.message_meter_values)
    assert Value.message_meter_values["transaction_id"] == -1

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_trigger_message_status_notification(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    clearTriggerMessage()
    response = await service.triggerMessage(event_loop, requested_message="MeterValues")
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(3)
    logging.info(Value.message_status_notification)
    assert Value.message_status_notification[0]["status"] == "Available"
    assert Value.message_status_notification[0]["connector_id"] == 0
    assert Value.message_status_notification[1]["status"] == "Preparing"
    assert Value.message_status_notification[1]["connector_id"] == 1

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_unlock_connector(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "UnlockFailed"

    await waitServerClose(server)


@pytest.mark.asyncio
async def test_update_firmware(event_loop):
    server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")
    while Value.bootnotification == 0:
        await asyncio.sleep(1)

    expiry_date = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    location = "http://gateway-enetestuk.autel.com/api/app-version-manager/version/upgrade/ota"
    clearTriggerMessage()
    response = await service.updateFirmware(event_loop, location, retrieve_date=expiry_date)
    status = await waitFirmwareStatus("Installed")
    assert status == "Installed"

    await waitServerClose(server)