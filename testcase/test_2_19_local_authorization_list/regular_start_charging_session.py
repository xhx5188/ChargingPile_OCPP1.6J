import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
import allure
from server.connect import waitConnectorStatus, clearTriggerMessage, waitRequest


@allure.feature("test_get_local_list_version_not_supported")
@pytest.mark.asyncio
async def test_get_local_list_version_not_supported(event_loop):
    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="true")
    assert response[0].status == "Accepted"

    # 改变配置信息"AuthorizationCacheEnabled"
    response = await service.changeConfiguration(event_loop, key="AuthorizationCacheEnabled", value="false")
    assert response[0].status == "Accepted" or response[0].status == "NotSupported"

    # 改变配置信息"LocalAuthListEnabled"
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="true")
    assert response[0].status == "Accepted"

    # 改变配置信息"AuthorizeRemoteTxRequests"
    response = await service.changeConfiguration(event_loop, key="AuthorizeRemoteTxRequests", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected"

    # 获取本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)

    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList1.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    logging.info("插枪")
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction")
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearTriggerMessage()
    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地开始充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "Remote"

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    logging.info("拔枪")
    Connector.unslot()
    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"