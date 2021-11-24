import asyncio
import json
import logging
import time
import pytest
import websockets
from ocpp.v16.enums import RegistrationStatus
from websockets.legacy.server import WebSocketServer

from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest, on_connect, waitServerClose, Value


@pytest.mark.skip(reason = "用例未完成")
@pytest.mark.asyncio
async def test_idle_charge_point(event_loop):
    pass


@pytest.mark.asyncio
async def test_connection_loss_during_transaction(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted

    # 插枪。。。

    # 等待充电桩状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 远程启动充电
    clearTriggerMessage()
    with open("./schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待本地发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 断开连接
    await waitServerClose(Value.server)

    # 重新建立连接
    clearTriggerMessage()
    Value.server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to old connections...")
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    flag, _ = await waitRequest("meter_values", 1)
    assert flag == True

    # 远程结束充电
    clearTriggerMessage()
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送结束充电请求
    flag, _ = await waitRequest("stop_transaction")
    assert flag == True
    logging.info("-" * 100)

    # 判断结束充电后枪的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪

    # 判断拔枪后枪的状态
    # status = await waitConnectorStatus(1, "Available")
    # assert status == "Available"


@pytest.mark.asyncio
async def test_offline_start_transaction_1(event_loop):
    # 改变配置信息"AllowOfflineTxForUnknowId"
    response = await service.changeConfiguration(event_loop, key="AllowOfflineTxForUnknowId", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"LocalAuthorizeOffline"
    response = await service.changeConfiguration(event_loop, key="LocalAuthorizeOffline", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 断开连接
    await waitServerClose(Value.server)

    # 用一张有效卡进行本地启动充电。。。


    # 重新建立连接
    clearTriggerMessage()
    Value.server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to old connections...")
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待本地发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 判断枪的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 本地主动发送停止充电请求。。。
    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg['reason'] == "Local"

    # 判断枪的停止充电后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪。。。

    # 判断拔枪后的状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.asyncio
async def test_offline_start_transaction_2(event_loop):
    # 改变配置信息"AllowOfflineTxForUnknowId"
    response = await service.changeConfiguration(event_loop, key="AllowOfflineTxForUnknowId", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"StopTransactionOnInvalidId"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnInvalidId", value="false")
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"LocalAuthorizeOffline"
    response = await service.changeConfiguration(event_loop, key="LocalAuthorizeOffline", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 断开连接
    await waitServerClose(Value.server)

    # 用一张无效卡进行本地启动充电。。。

    # 重新建立连接
    clearTriggerMessage()
    Value.server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to old connections...")
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待本地发送充电请求
    flag, msg = await waitRequest("start_transaction")
    assert flag == True
    assert msg['idTagInfo']['status'] == "Invalid"

    # 判断枪的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    # 本地主动发送停止充电请求。。。
    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg['reason'] == "Local"

    # 判断枪的停止充电后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪。。。

    # 判断拔枪后的状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.asyncio
async def test_offline_start_transaction_3(event_loop):
    # 改变配置信息"AllowOfflineTxForUnknowId"
    response = await service.changeConfiguration(event_loop, key="AllowOfflineTxForUnknowId", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"StopTransactionOnInvalidId"
    response = await service.changeConfiguration(event_loop, key="StopTransactionOnInvalidId", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"LocalAuthorizeOffline"
    response = await service.changeConfiguration(event_loop, key="LocalAuthorizeOffline", value="true")
    assert response[0].status == RegistrationStatus.accepted

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 断开连接
    await waitServerClose(Value.server)

    # 用一张无效卡进行本地启动充电。。。

    # 重新建立连接
    clearTriggerMessage()
    Value.server: WebSocketServer = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to old connections...")
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 等待本地发送充电请求
    flag, msg = await waitRequest("start_transaction")
    assert flag == True
    assert msg['idTagInfo']['status'] == "Invalid"

    # 判断枪的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"


    flag, msg = await waitRequest("stop_transaction")
    assert flag == True
    assert msg['reason'] == "DeAuthorized"

    # 判断枪的停止充电后的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪。。。

    # 判断拔枪后的状态
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.asyncio
async def test_stop_transaction(event_loop):
    
