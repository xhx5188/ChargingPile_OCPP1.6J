import asyncio
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import waitConnectorStatus, waitRequest


@pytest.mark.need_swipe_card
@allure.feature("test_regular_charging_session1")
@pytest.mark.asyncio
async def test_regular_charging_session1(event_loop):
    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="5")
    assert response[0].status == RegistrationStatus.accepted

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

    # 等待本地发送测量信息
    flag, _ = await waitRequest("meter_values")
    assert flag == True

    logging.info("[请刷再次刷卡停止充电:]")

    # 等待本地结束充电
    flag, _ = await waitRequest("stop_transaction", 40)
    assert flag == True

    # 等待本地停止充电成功
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪
    logging.info("拔枪")
    Connector.unslot()
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.need_swipe_card
@allure.feature("test_regular_charging_session2")
@pytest.mark.asyncio
async def test_regular_charging_session2(event_loop):
    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="10")
    assert response[0].status == RegistrationStatus.accepted

    # 刷卡
    logging.info("[请刷一张未绑定卡启动充电:]")

    # 等待充电桩鉴权
    logging.info("等待鉴权")
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 插枪
    logging.info("插枪")
    Connector.slot()

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    logging.info("[请刷再次刷卡停止充电:]")

    # 等待本地停止充电
    flag, _ = await waitRequest("stop_transaction", 40)
    assert flag == True

    # 等待本地停止充电成功
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 拔枪
    logging.info("拔枪")
    Connector.unslot()
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@pytest.mark.need_swipe_card
@allure.feature("test_regular_charging_session3")
@pytest.mark.asyncio
async def test_regular_charging_session3(event_loop):
    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"ConnectionTimeOut"
    response = await service.changeConfiguration(event_loop, key="ConnectionTimeOut", value="30")
    assert response[0].status == RegistrationStatus.accepted

    # 刷卡
    logging.info("[请刷一张未绑定卡启动充电:]")

    # 等待充电桩鉴权
    logging.info("等待鉴权")
    flag, msg = await waitRequest("authorize", 40)
    assert flag == True

    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    status = await waitConnectorStatus(1, "Available", 30)
    assert status == "Available"




