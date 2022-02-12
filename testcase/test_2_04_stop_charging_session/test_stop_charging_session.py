import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import waitConnectorStatus, waitRequest, clearTriggerMessage, Value


@pytest.mark.need_swipe_card
@allure.feature("test_stop_transaction1")
@pytest.mark.asyncio
@pytest.mark.socket
async def test_stop_transaction1(event_loop):
    # 插枪
    logging.info("插枪")
    Connector.slot()
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 刷卡
    logging.info("[请刷一张未绑定卡启动充电:]")

    # 等待充电桩鉴权
    logging.info("等待鉴权")
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待本地启动充电成功
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    logging.info("[请刷另一张卡停止充电:]")

    # 等待充电桩鉴权
    logging.info("等待鉴权")
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    # 等待本地开始充电
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@pytest.mark.need_swipe_card
@allure.feature("test_stop_transaction2")
@pytest.mark.asyncio
@pytest.mark.socket
async def test_stop_transaction2(event_loop):
    # 插枪
    logging.info("插枪")
    Connector.slot()
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 刷卡
    logging.info("[请刷一张未绑定卡启动充电:]")

    # 等待充电桩鉴权
    logging.info("等待鉴权")
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待本地启动充电成功
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    logging.info("[请刷另一张卡停止充电:]")

    # 等待充电桩鉴权
    logging.info("等待鉴权")
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    # 等待本地开始充电
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"


@allure.feature("test_EV_side_disconnected1")
@pytest.mark.asyncio
@pytest.mark.socket
async def test_EV_side_disconnected1(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MinimumStatusDuration"
    response = await service.changeConfiguration(event_loop, key="MinimumStatusDuration", value="0")
    assert response[0].status == "Accepted" or response[0].status == "NotSupported"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"StopTransactionOnEVSideDisconnect"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnEVSideDisconnect", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected" or response[0].status == "NotSupported"

    # 改变配置信息"StopTransactionOnEVSideDisconnect"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnEVSideDisconnect", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected"

    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
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

    # 等待本地开始充电
    flag, msg = await waitRequest("start_transaction")
    assert flag == True
    logging.info(msg)

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearTriggerMessage()

    # 拔枪
    Connector.unslot()

    # 等待本地结束充电
    flag, msg = await waitRequest("stop_transaction")
    logging.info(msg)
    assert flag == True
    assert msg['reason'] == "EVDisconnected"

    # status = await waitConnectorStatus(1, "Finishing")
    # assert status == "Finishing"

    flag, msg = await waitRequest("status_notification")
    logging.info(flag)
    logging.info(msg)  #ev side disconnected


@allure.feature("test_EV_side_disconnected2_1")
@pytest.mark.asyncio
async def test_EV_side_disconnected2_1(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MinimumStatusDuration"
    response = await service.changeConfiguration(event_loop, key="MinimumStatusDuration", value="0")
    assert response[0].status == "Accepted" or response[0].status == "NotSupported"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"StopTransactionOnEVSideDisconnect"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnEVSideDisconnect", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected" or response[0].status == "NotSupported"

    response = await service.changeConfiguration(event_loop, key="UnlockConnectorOnEVSideDisconnect", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected"

    logging.info("插枪")
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

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

    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待本地开始充电
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    logging.info("拔枪")
    Connector.unslot()

    flag, msg = await waitRequest("stop_transaction")
    assert msg['reason'] == "EVDisconnected"
    assert flag == True

    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 解锁抢
    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "Unlocked" or response[0].status == "NotSupported"


@allure.feature("test_EV_side_disconnected2_2")
@pytest.mark.asyncio
@pytest.mark.socket
async def test_EV_side_disconnected2_2(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MinimumStatusDuration"
    response = await service.changeConfiguration(event_loop, key="MinimumStatusDuration", value="0")
    assert response[0].status == "Accepted" or response[0].status == "NotSupported"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"StopTransactionOnEVSideDisconnect"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnEVSideDisconnect", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected" or response[0].status == "NotSupported"

    response = await service.changeConfiguration(event_loop, key="UnlockConnectorOnEVSideDisconnect", value="true")
    assert response[0].status == "Accepted" or response[0].status == "Rejected"

    logging.info("插枪")
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

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

    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 等待本地开始充电
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    logging.info("拔枪")
    Connector.unslot()

    flag, msg = await waitRequest("stop_transaction")
    assert msg['reason'] == "EVDisconnected"
    assert flag == True

    flag, msg = await waitRequest("status_notification")
    logging.info(msg)
    assert flag == True
    assert msg["status"] == "Finishing"
    assert msg["info"] == "EV side disconnected"

    # 解锁抢
    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "Unlocked" or response[0].status == "NotSupported"

    logging.info("拔枪")
    Connector.slot()

    # 等待枪恢复可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@allure.feature("test_EV_side_disconnected3")
@pytest.mark.asyncio
@pytest.mark.socket
async def test_EV_side_disconnected3(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MinimumStatusDuration"
    response = await service.changeConfiguration(event_loop, key="MinimumStatusDuration", value="0")
    assert response[0].status == "Accepted" or response[0].status == "NotSupported"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    response = await service.changeConfiguration(event_loop, key="UnlockConnectorOnEVSideDisconnect", value="false")
    assert response[0].status == "Accepted" or response[0].status == "Rejected"

    # 改变配置信息"StopTransactionOnEVSideDisconnect"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnEVSideDisconnect", value="false")
    assert response[0].status == "Rejected" #产品定义，拔枪之后必须结束订单。所以StopTransactionOnEVSideDisconnect不能设置为false

    # 经庞子乐确认，后面的流程不往下走
    # logging.info("插枪")
    # Connector.slot()
    #
    # # 获取桩充电之前的状态
    # status = await waitConnectorStatus(1, "Preparing")
    # assert status == "Preparing"
    #
    # clearTriggerMessage()
    # with open("../schema/RemoteStartTransaction.json", 'r') as f:
    #     data = json.load(f)
    # response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
    #                                                 connector_id=data.get('connectorId'),
    #                                                 charging_profile=data.get('chargingProfile'))
    # assert response[0].status == RegistrationStatus.accepted
    #
    # # 等待充电桩鉴权
    # flag, _ = await waitRequest("authorize")
    # assert flag == True
    #
    # flag, _ = await waitRequest("start_transaction")
    # assert flag == True
    #
    # # 等待本地开始充电
    # status = await waitConnectorStatus(1, "Charging")
    # assert status == "Charging"
    #
    # logging.info("拔枪")
    # Connector.unslot()
    #
    # # # 校验充电时拔枪后的状态
    # # status = await waitConnectorStatus(1, "SuspendedEV", 40)
    # # assert status == "SuspendedEV" or status == "SuspendedEVSE"
    #
    # flag, msg = await waitRequest("status_notification")
    # assert flag == True
    # logging.info(msg)
    #
    # # 结束远程充电
    # response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
    # assert response[0].status == RegistrationStatus.accepted
    # status = await waitConnectorStatus(1, "Available")
    # assert status == "Available"
    #
    # flag, msg = await waitRequest("stop_transaction")
    # assert flag == True
    # assert msg["reason"] == "Remote"
    #
    # logging.info("拔枪")
    # Connector.slot()
    #
    # # 等待枪恢复可用
    # status = await waitConnectorStatus(1, "Available")
    # assert status == "Available"



