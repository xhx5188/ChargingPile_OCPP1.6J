import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
from connector.connector import Connector


@allure.feature("test_hard_reset_without_transaction")
@pytest.mark.asyncio
async def test_hard_reset_without_transaction(event_loop):
    #远程设置桩为不可用
    response = await service.changeAvailability(event_loop, connector_id=1, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    #重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Hard")
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    #判断重启之后桩的状态仍不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"

    # 远程设置桩为可用
    response = await service.changeAvailability(event_loop, connector_id=1, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@allure.feature("test_soft_reset_without_transaction")
@pytest.mark.asyncio
async def test_soft_reset_without_transaction(event_loop):
    # 远程设置桩为不可用
    response = await service.changeAvailability(event_loop, connector_id=1, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    # 重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Soft")
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩重启
    flag, _ = await waitRequest("boot_notification", 100)
    assert flag == True

    # 判断重启之后桩的状态仍不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"

    # 远程设置桩为可用
    response = await service.changeAvailability(event_loop, connector_id=1, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@allure.feature("test_hard_reset_with_transaction")
@pytest.mark.asyncio
async def test_hard_reset_with_transaction(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="15")
    assert response[0].status == RegistrationStatus.accepted

    # 插枪
    Connector.slot()

    #等待桩状态为可用
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

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    #重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Hard")
    assert response[0].status == RegistrationStatus.accepted

    #等待结束充电
    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg["reason"] == "HardReset"

    # 等待桩发送Finishing
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    #等待充电桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待桩状态为可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@allure.feature("test_soft_reset_with_transaction")
@pytest.mark.asyncio
async def test_soft_reset_with_transaction(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="2")
    assert response[0].status == RegistrationStatus.accepted

    # 插枪
    Connector.slot()

    # 等待桩状态为可用
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

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 重启充电桩
    clearTriggerMessage()
    response = await service.reset(event_loop, "Soft")
    assert response[0].status == RegistrationStatus.accepted

    # 等待结束充电
    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg["reason"] == "SoftReset"

    # 等待桩发送Preparing
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 等待充电桩重启
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待桩状态为可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"
