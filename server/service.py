import asyncio
from ocpp.v16 import call
from server.connect import Value, clearTriggerMessage

async def remoteStartTransaction(event_loop, id_tag: str, connector_id: int = None, charging_profile: dict = None):
    Value.transactionId = charging_profile['transactionId']
    request = call.RemoteStartTransactionPayload(id_tag, connector_id, charging_profile)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def remoteStopTransaction(event_loop, transaction_id: int):
    request = call.RemoteStopTransactionPayload(transaction_id)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def changeAvailability(event_loop, connector_id: int, type: str):
    request = call.ChangeAvailabilityPayload(connector_id, type)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def getConfiguration(event_loop, key: list = None):
    request = call.GetConfigurationPayload(key)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    result = response[0].configuration_key
    return result

async def changeConfiguration(event_loop, key: str, value):
    request = call.ChangeConfigurationPayload(key, value)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response

async def clearCache(event_loop):
    request = call.ClearCachePayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def setChargingProfile(event_loop, connector_id: int, cs_charging_profiles: dict):
    request = call.SetChargingProfilePayload(connector_id, cs_charging_profiles)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def clearChargeProfile(event_loop, id: int = None, connector_id: int = None,
                                charging_profile_purpose = None, stack_level: int = None):
    request = call.ClearChargingProfilePayload(id, connector_id, charging_profile_purpose, stack_level)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def dataTransfer(event_loop, vendor_id: str, message_id: str = None, data: str = None):
    clearTriggerMessage()
    request = call.DataTransferPayload(vendor_id, message_id, data)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def getCompositeSchedule(event_loop, connector_id: int, duration: int, charging_rate_unit: None):
    request = call.GetCompositeSchedulePayload(connector_id, duration, charging_rate_unit)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def getDiagnostics(event_loop, location: str, retries: int = None, retry_interval: int = None,
                            start_time: str = None, stop_time: str = None):
    request = call.GetDiagnosticsPayload(location, retries, retries, start_time, stop_time)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def sendLocalList(event_loop, list_version: int, update_type, local_authorization_list: list):
    request = call.SendLocalListPayload(list_version, update_type, local_authorization_list)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def getLocalList(event_loop):
    request = call.GetLocalListVersionPayload()
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def reserveNow(event_loop, connector_id: int, expiry_date: str, id_tag: str,
                        reservation_id: int, parent_id_tag: str = None):
    request = call.ReserveNowPayload(connector_id, expiry_date, id_tag, reservation_id)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def reset(event_loop, type: str):
    request = call.ResetPayload(type)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def triggerMessage(event_loop, requested_message, connector_id: int = None):
    request = call.TriggerMessagePayload(requested_message, connector_id)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def unlockConnector(event_loop, connector_id: int):
    request = call.UnlockConnectorPayload(connector_id)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response


async def updateFirmware(event_loop, location: str, retrieve_date: str, retries: int = None,
                                        retry_interval: int = None):
    request = call.UpdateFirmwarePayload(location, retrieve_date, retries, retry_interval)
    tasks = [event_loop.create_task(Value.chargePoint.call(request))]
    response = await asyncio.gather(*tasks)
    return response