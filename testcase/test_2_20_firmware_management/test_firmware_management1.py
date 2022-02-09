import asyncio
import logging
from datetime import datetime, timedelta
import pytest
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


# 充电桩在Unavailable状态下出发远程升级
@allure.feature("test_firmware_update_unavailable")
@pytest.mark.asyncio
async def test_firmware_update_unavailable(event_loop):
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