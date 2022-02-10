import asyncio
import logging
from datetime import datetime, timedelta
import pytest
from ocpp.v16.enums import RegistrationStatus

from connector.connector import Connector
from server import service
import allure
from server.connect import waitRequest, waitConnectorStatus, clearTriggerMessage


# 充电桩在Available状态下出发远程升级
@allure.feature("test_firmware_update_available")
@pytest.mark.asyncio
async def test_firmware_update_available(event_loop):
    # 充电桩刚开始即为available状态

    clearTriggerMessage()
    uri = "https://gateway-enetestuk.autel.com/api/app-version-manager/version/upgrade/ota" #英国测试环境
    retrieve_date = (datetime.utcnow() + timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.updateFirmware(event_loop, uri, retrieve_date)
    logging.info(response[0])

    # 等待充电桩被设置为不可用状态
    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    logging.info(flag, msg)
    assert flag == True
    assert msg["status"] == "Downloading"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Downloaded"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installing"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installed"

    flag, msg = await waitRequest("boot_notification", 400)
    assert flag == True

    # 等待充电桩被设置为可用状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


# 充电桩在Unavailable状态下触发远程升级
@allure.feature("test_firmware_update_unavailable1")
@pytest.mark.asyncio
async def test_firmware_update_unavailable1(event_loop):
    # 先设置桩不可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Inoperative")
    assert response[0].status == "Accepted"

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    clearTriggerMessage()
    uri = "https://gateway-enetestuk.autel.com/api/app-version-manager/version/upgrade/ota"  # 英国测试环境
    retrieve_date = (datetime.utcnow() + timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.updateFirmware(event_loop, uri, retrieve_date)
    logging.info(response[0])

    flag, msg = await waitRequest("firmware_status_notification", 400)
    logging.info(flag, msg)
    assert flag == True
    assert msg["status"] == "Downloading"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Downloaded"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installing"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installed"

    flag, msg = await waitRequest("boot_notification", 400)
    assert flag == True

    # 等待充电桩被设置为可用状态
    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"


# 充电桩的枪在Unavailable状态下触发远程升级
@allure.feature("test_firmware_update_unavailable2")
@pytest.mark.asyncio
async def test_firmware_update_unavailable2(event_loop):
    # 先设置桩不可用
    response = await service.changeAvailability(event_loop, connector_id=1, type="Inoperative")
    assert response[0].status == "Accepted"

    # 等待充电桩状态
    # status = await waitConnectorStatus(0, "Available")
    # assert status == "Available"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    clearTriggerMessage()
    uri = "https://gateway-enetestuk.autel.com/api/app-version-manager/version/upgrade/ota"  # 英国测试环境
    retrieve_date = (datetime.utcnow() + timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.updateFirmware(event_loop, uri, retrieve_date)
    logging.info(response[0])

    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    logging.info(flag, msg)
    assert flag == True
    assert msg["status"] == "Downloading"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Downloaded"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installing"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installed"

    flag, msg = await waitRequest("boot_notification", 400)
    assert flag == True

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"


# 充电桩在Faulted状态(接地错误)下出发远程升级
@pytest.mark.skip("需要模拟故障")
@allure.feature("test_firmware_update_faulted")
@pytest.mark.asyncio
async def test_firmware_update_faulted(event_loop):
    # 模拟充电桩faulted状态。。。

    clearTriggerMessage()
    uri = "https://gateway-enetestuk.autel.com/api/app-version-manager/version/upgrade/ota" #英国测试环境
    retrieve_date = (datetime.utcnow() + timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.updateFirmware(event_loop, uri, retrieve_date)
    logging.info(response[0])

    # # 等待充电桩被设置为不可用状态
    # status = await waitConnectorStatus(0, "Unavailable")
    # assert status == "Unavailable"
    # status = await waitConnectorStatus(1, "Unavailable")
    # assert status == "Unavailable"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    logging.info(flag, msg)
    assert flag == True
    assert msg["status"] == "Downloading"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Downloaded"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installing"

    flag, msg = await waitRequest("firmware_status_notification", 400)
    assert flag == True
    assert msg["status"] == "Installed"

    flag, msg = await waitRequest("boot_notification", 400)
    assert flag == True

    # # 等待充电桩被设置为可用状态
    # status = await waitConnectorStatus(0, "Available")
    # assert status == "Available"
    # status = await waitConnectorStatus(1, "Available")
    # assert status == "Available"

# 充电桩的枪在Preparing状态下触发远程升级
@allure.feature("test_firmware_update_preparing")
@pytest.mark.asyncio
async def test_firmware_update_preparing(event_loop):
    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    clearTriggerMessage()
    uri = "https://gateway-enetestuk.autel.com/api/app-version-manager/version/upgrade/ota"  # 英国测试环境
    retrieve_date = (datetime.utcnow() + timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.updateFirmware(event_loop, uri, retrieve_date)
    # assert response[0].status == RegistrationStatus.rejected
    logging.info(response)
    await asyncio.sleep(30)