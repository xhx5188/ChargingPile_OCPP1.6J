import logging
import pytest
import websockets
from ocpp.v16.enums import RegistrationStatus
from websockets.legacy.server import WebSocketServer
from server import service
from server.connect import waitConnectorStatus, waitRequest, Value
from testcase.test_2_02_cold_boot_charge_point.conftest import Val, on_connect_boot_reject, on_connect_boot_pending
from dateutil.parser import parse
import allure

@allure.feature("test_cold_boot_charge_point")
@pytest.mark.asyncio
async def test_cold_boot_charge_point(event_loop):
    Value.server: WebSocketServer = await websockets.serve(on_connect_boot_reject, \
                                                           '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")

    # 等待bootnotification
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    #拒绝客户端的bootnotification请求三次
    assert Val.boot_reject_count == 3

    # 获取桩的状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    #等待枪1可用
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 等待心跳
    flag, msg = await waitRequest("heartbeat")
    assert flag == True
    time1 = parse(msg['timestamp'])

    # 等待心跳
    flag, msg = await waitRequest("heartbeat")
    assert flag == True
    time2 = parse(msg['timestamp'])

    interval = (time2 - time1).seconds
    logging.info("actual interval1 = %s" % interval)
    assert abs(interval - Val.interval) <= 1

    # 等待心跳
    flag, msg = await waitRequest("heartbeat")
    assert flag == True
    time3 = parse(msg['timestamp'])

    interval = (time3 - time2).seconds
    logging.info("acutal interval2 = %s" % interval)
    assert abs(interval - Val.interval) <= 1


@allure.feature("test_cold_boot_charge_point_pending")
@pytest.mark.asyncio
async def test_cold_boot_charge_point_pending(event_loop):
    Value.server: WebSocketServer = await websockets.serve(on_connect_boot_pending, \
                                                           '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("Server Started listening to new connections...")

    # 等待bootnotification
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 获取配置信息
    result = await service.getConfiguration(event_loop)
    logging.info(result)

    Val.flag_pend = False
    # 改变配置信息"MeterValueSampleInterval"
    value = "4"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value=value)
    assert response[0].status == RegistrationStatus.accepted

    # 等待bootnotification
    flag, _ = await waitRequest("boot_notification")
    assert flag == True

    # 获取桩的状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    # 等待心跳
    flag, msg = await waitRequest("heartbeat")
    assert flag == True
    time1 = parse(msg['timestamp'])

    # 等待心跳
    flag, msg = await waitRequest("heartbeat")
    assert flag == True
    time2 = parse(msg['timestamp'])

    interval = (time2 - time1).seconds
    logging.info("actual interval1 = %s" % interval)
    assert abs(interval - Val.interval) <= 1

    # 等待心跳
    flag, msg = await waitRequest("heartbeat")
    assert flag == True
    time3 = parse(msg['timestamp'])

    interval = (time3 - time2).seconds
    logging.info("acutal interval2 = %s" % interval)
    assert abs(interval - Val.interval) <= 1







