import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
import allure


@pytest.mark.need_swipe_card
@allure.feature("test_start_charging_session_authorize_invalid")
@pytest.mark.asyncio
async def test_start_charging_session_authorize_invalid(event_loop):
    # 改变配置信息"MinimumStatusDuration"
    response = await service.changeConfiguration(event_loop, key="MinimumStatusDuration", value="3")
    assert response[0].status == "Accepted" or response[0].status == "NotSupported"

    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 插枪
    Connector.slot()

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 刷卡
    logging.info("[请刷一张未绑定卡启动充电:]")

    # 等待认证失败
    flag, msg = await waitRequest("authorize")
    assert flag == True
    logging.info(msg)
    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == False


@allure.feature("test_start_charging_session_lock_failure")
@pytest.mark.skip(reason="需要socket版本的桩")
@pytest.mark.asyncio
async def test_start_charging_session_lock_failure(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

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

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # EV driver plugs in the cable halfway...
    # 测试锁失败，半途插枪，需要socket版本的桩。
    # 最好可以让socket版本的桩的锁不能锁住，找硬件他们给一个模拟。
