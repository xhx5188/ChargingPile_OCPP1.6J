import asyncio
import logging
from datetime import datetime, timedelta
import pytest
from connector.connector import Connector
from server import service
import allure
from server.connect import waitRequest, waitConnectorStatus, clearTriggerMessage


@allure.feature("test_download_and_install")
@pytest.mark.asyncio
async def test_download_and_install(event_loop):
    clearTriggerMessage()
    # uri = "https://autel-cloud-energy-gateway-enetest.auteltech.cn/api/app-version-manager/version/upgrade/ota" #中国测试环境
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


@allure.feature("test_download_failed")
@pytest.mark.asyncio
async def test_download_failed(event_loop):
    uri = "ftp://google.com"
    retrieve_date = (datetime.utcnow() + timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.updateFirmware(event_loop, uri, retrieve_date, retries = 0)
    logging.info(response[0])

    # 等待充电桩被设置为不可用状态
    status = await waitConnectorStatus(0, "Unavailable")
    assert status == "Unavailable"
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    flag, msg = await waitRequest("firmware_status_notification", 100)
    # logging.info(flag, msg)
    assert flag == True
    assert msg["status"] == "DownloadFailed"

    # 等待充电桩恢复为可用状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"


@allure.feature("test_installation_failed")
@pytest.mark.asyncio
async def test_installation_failed(event_loop):
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

    clearTriggerMessage()
    # 掉电
    logging.info("掉电")
    Connector.unelectricity()

    await asyncio.sleep(30)

    clearTriggerMessage()
    # 上电
    logging.info("上电")
    Connector.electricity()

    # 等待桩重启
    flag, _ = await waitRequest("boot_notification", 50)
    assert flag == True

    # 本地发送固件安装失败通知
    flag, msg = await waitRequest("firmware_status_notification", 100)
    assert flag == True
    assert msg["status"] == "InstallationFailed"

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"
