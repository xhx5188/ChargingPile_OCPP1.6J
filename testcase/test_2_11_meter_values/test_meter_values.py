import asyncio
import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest, Value
from dateutil.parser import parse


@allure.feature("test_sampled_meter_values")
@pytest.mark.asyncio
async def test_sampled_meter_values(event_loop):
    # 改变配置信息"MeterValueSampleInterval"
    set_interval = 5
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value=str(set_interval))
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"ClockAlignedDataInterval"
    response = await service.changeConfiguration(event_loop, key="ClockAlignedDataInterval", value="0")
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"MeterValuesSampledData"
    result = await service.getConfiguration(event_loop, ["MeterValuesSampledData"])
    logging.info(result)
    # assert result[0]['value'] == str(set_interval)

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    clearTriggerMessage()
    # 插枪
    Connector.slot()

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    logging.info(msg)
    assert flag == True
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 等待充电桩发送测量信息
    clearTriggerMessage()
    _, msg = await waitRequest("meter_values")
    logging.info(msg)
    time1 = parse(msg["meter_value"][0]["timestamp"])

    # 等待充电桩发送测量信息
    clearTriggerMessage()
    _, msg = await waitRequest("meter_values")
    logging.info(msg)
    time2 = parse(msg["meter_value"][0]["timestamp"])

    interval = (time2 - time1).seconds
    assert abs(interval - set_interval) <= 1

    # 等待充电桩发送测量信息
    clearTriggerMessage()
    _, msg = await waitRequest("meter_values")
    logging.info(msg)
    time3 = parse(msg["meter_value"][0]["timestamp"])

    interval = (time3 - time2).seconds
    assert abs(interval - set_interval) <= 1

    # 结束充电
    response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
    assert response[0].status == RegistrationStatus.accepted

    # 获取结束充电后枪的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@allure.feature("test_clock_aligned_meter_values")
@pytest.mark.asyncio
async def test_clock_aligned_meter_values(event_loop):
    # 改变配置信息"ClockAlignedDataInterval"
    set_interval = 120
    response = await service.changeConfiguration(event_loop, key="ClockAlignedDataInterval", value=str(set_interval))
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="0")
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"MeterValueAlignedData"
    result = await service.getConfiguration(event_loop, ["MeterValueAlignedData"])
    logging.info(result)

    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 插枪
    Connector.slot()

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    assert flag == True
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 等待充电桩发送测量信息
    clearTriggerMessage()
    _, msg = await waitRequest("meter_values")
    logging.info("-" * 100)
    logging.info(msg)
    time1 = parse(msg["meter_value"][0]["timestamp"])

    # 等待充电桩发送测量信息
    clearTriggerMessage()
    _, msg = await waitRequest("meter_values")
    logging.info("-" * 100)
    logging.info(msg)
    time2 = parse(msg["meter_value"][0]["timestamp"])

    interval = (time2 - time1).seconds
    assert abs(interval - 10) <= 1

    # 等待充电桩发送测量信息
    clearTriggerMessage()
    _, msg = await waitRequest("meter_values")
    logging.info("-" * 100)
    logging.info(msg)
    time3 = parse(msg["meter_value"][0]["timestamp"])

    interval = (time3 - time2).seconds
    assert abs(interval - 10) <= 1

    # await asyncio.sleep(600)

    # 结束充电
    response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送结束充电请求
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"
