import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest, Value
import allure


@allure.feature("test_charging_with_connector1_1")
@pytest.mark.asyncio
async def test_charging_with_connector1_1(event_loop):
    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction1_1.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    assert flag == True
    logging.info(msg)
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction", 100)
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(1, "Finishing")
    assert status == "Finishing"



@allure.feature("test_charging_with_connector1_2")
@pytest.mark.asyncio
async def test_charging_with_connector1_2(event_loop):
    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing", 30)
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction1_2.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    assert flag == True
    logging.info(msg)
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction", 50)
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(1, "Finishing")
    assert status == "Finishing"


@allure.feature("test_charging_with_connector2_1")
@pytest.mark.asyncio
async def test_charging_with_connector2_1(event_loop):
    # 获取桩充电之前的状态
    status = await waitConnectorStatus(2, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction2_1.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    assert flag == True
    logging.info(msg)
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction", 100)
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(2, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(2, "Finishing")
    assert status == "Finishing"


@allure.feature("test_charging_with_connector2_2")
@pytest.mark.asyncio
async def test_charging_with_connector2_2(event_loop):
    # 获取桩充电之前的状态
    status = await waitConnectorStatus(2, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction2_2.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize")
    assert flag == True
    logging.info(msg)
    assert msg['id_tag'] == data.get('idTag')

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction", 60)
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(2, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(2, "Finishing")
    assert status == "Finishing"


@allure.feature("test_charging_with_all_connector")
@pytest.mark.asyncio
async def test_charging_with_all_connector(event_loop):
    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    status = await waitConnectorStatus(2, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("../schema/RemoteStartTransaction1_2.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'))
    assert response[0].status == RegistrationStatus.accepted

    with open("../schema/RemoteStartTransaction2_2.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权两次
    flag, msg = await waitRequest("authorize")
    assert flag == True
    flag, msg = await waitRequest("authorize")
    assert flag == True

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction", 60)
    assert flag == True
    flag, msg = await waitRequest("start_transaction", 60)
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging", 50)
    assert status == "Charging"
    status = await waitConnectorStatus(2, "Charging", 50)
    assert status == "Charging"

    logging.info("结束充电")
    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
    assert response[0].status == RegistrationStatus.accepted
    response = await service.remoteStopTransaction(event_loop, Value.transactionId_2)
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩结束充电之后的状态
    status = await waitConnectorStatus(1, "Finishing")
    assert status == "Finishing"
    status = await waitConnectorStatus(2, "Finishing")
    assert status == "Finishing"