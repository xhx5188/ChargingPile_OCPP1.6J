import asyncio
import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
import allure


@allure.feature("test_power_failure1")
@pytest.mark.asyncio
@pytest.mark.need_power_down
async def test_power_failure1(event_loop):
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
    logging.info("[请掉电。。。]")
    await asyncio.sleep(60)

    # 掉电后等待充电桩发送结束充电请求
    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg['reason'] == "PowerLoss"

    # 掉电后等待充电桩的状态
    status = await waitConnectorStatus(1, "Finishing")
    assert status == "Faulted"

    await asyncio.sleep(30)

    # 上电
    logging.info("请上电。。。")
    await asyncio.sleep(60)

    # 等待桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@allure.feature("test_power_failure2")
@pytest.mark.asyncio
@pytest.mark.need_power_down
async def test_power_failure2(event_loop):
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
    logging.info("[请掉电。。。]")
    await asyncio.sleep(60)

    await asyncio.sleep(30)

    # 上电
    logging.info("[请上电。。。]")
    await asyncio.sleep(60)

    # 等待桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 掉电后等待充电桩发送结束充电请求
    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg['reason'] == "PowerLoss"


@allure.feature("test_power_failure3")
@pytest.mark.asyncio
@pytest.mark.need_power_down
@pytest.mark.need_power_down
async def test_power_failure3(event_loop):
    # 远程设置桩为不可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    clearTriggerMessage()
    # 掉电
    logging.info("[请掉电。。。]")
    await asyncio.sleep(60)

    # 上电
    logging.info("[请上电。。。]")
    await asyncio.sleep(60)

    # 等待桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    # 远程设置桩为可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"



