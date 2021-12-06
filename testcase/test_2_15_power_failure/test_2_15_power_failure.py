import asyncio
import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
import allure


@allure.feature("test_power_failure_stop_transaction_before_going_down")
@pytest.mark.asyncio
async def test_power_failure_stop_transaction_before_going_down(event_loop):
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
    with open("../test_2_08_resetting_happy_flow/schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待充电桩发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearTriggerMessage()
    # 掉电
    Connector.unelectricity()

    # 掉电后等待充电桩发送结束充电请求
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    # 掉电后等待充电桩的状态
    status = await waitConnectorStatus(1, "Finishing")
    assert status == "Finishing"

    await asyncio.sleep(30)

    # 上电
    Connector.electricity()

    # 等待桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@allure.feature("test_power_failure_stop_transaction")
@pytest.mark.asyncio
async def test_power_failure_stop_transaction(event_loop):
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
    with open("../test_2_08_resetting_happy_flow/schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待充电桩发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    seconds = 1
    # 掉电
    logging.info("掉电")
    Connector.unelectricity()
    logging.info("掉电后等待%s秒" % seconds)
    await asyncio.sleep(seconds)

    # 等待充电桩发送结束充电请求
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    # 上电
    logging.info("重新上电")
    clearTriggerMessage()
    Connector.electricity()

    # 等待桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


    # 掉电后等待充电桩的状态
    status = await waitConnectorStatus(1, "Finishing")
    assert status == "Finishing"


@allure.feature("test_power_failure_with_unavailable_status")
@pytest.mark.asyncio
async def test_power_failure_with_unavailable_status(event_loop):
    pass


