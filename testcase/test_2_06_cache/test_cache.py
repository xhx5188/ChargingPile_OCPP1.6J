import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import waitConnectorStatus, waitRequest, clearTriggerMessage


@allure.feature("test_regular_start_charging_session")
@pytest.mark.asyncio
async def test_regular_start_charging_session(event_loop):
    # 改变配置信息"AuthorizationCacheEnabled"
    response = await service.changeConfiguration(event_loop, key="AuthorizationCacheEnabled", value="true")
    assert response[0].status == "Accepted"

    # 改变配置信息"AuthorizeRemoteTxRequests"
    response = await service.changeConfiguration(event_loop, key="AuthorizeRemoteTxRequests", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected"

    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="true")
    assert response[0].status == "Accepted"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    logging.info("插枪")
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待本地开始充电
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    logging.info("拔枪")
    Connector.unslot()

    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    logging.info("插枪")
    Connector.slot()

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待本地开始充电
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    logging.info("拔枪")
    Connector.unslot()

    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.need_swipe_card
@allure.feature("test_clear_authorization_data_in_authorization_cache")
@pytest.mark.asyncio
async def test_clear_authorization_data_in_authorization_cache(event_loop):
    # 改变配置信息"AuthorizationCacheEnabled"
    response = await service.changeConfiguration(event_loop, key="AuthorizationCacheEnabled", value="true")
    assert response[0].status == "Accepted"

    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="true")
    assert response[0].status == "Accepted"

    # 改变配置信息"ConnectionTimeOut"
    response = await service.changeConfiguration(event_loop, key="ConnectionTimeOut", value="60")
    assert response[0].status == "Accepted"

    # 刷卡
    logging.info("[请刷一张未绑定卡:]")

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 未插枪，超时后枪恢复Available状态
    status = await waitConnectorStatus(1, "Available", 30)
    assert status == "Available"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 刷卡
    logging.info("[请刷一张未绑定卡:]")

    # 等待充电桩鉴权
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 未插枪，超时后枪恢复Available状态
    status = await waitConnectorStatus(1, "Available", 30)
    assert status == "Available"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted