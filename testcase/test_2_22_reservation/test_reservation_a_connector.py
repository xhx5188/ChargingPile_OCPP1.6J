import asyncio
import json
import logging
from datetime import datetime, timedelta
import pytest
from ocpp.v16.enums import RegistrationStatus

from connector.connector import Connector
from server import service
from server.config import GetCfg
from server.connect import waitConnectorStatus, waitRequest, clearTriggerMessage
import allure


@allure.feature("test_local_start_transaction")
# @pytest.mark.skip("需要刷卡")
@pytest.mark.asyncio
async def test_local_start_transaction(event_loop):
    expiry_date = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.reserveNow(event_loop, connector_id=1, expiry_date=expiry_date,
                                        id_tag=GetCfg.get_id_tag(), reservation_id=1)
    logging.info(response)
    assert response[0].status == RegistrationStatus.accepted

    # 获取枪状态
    status = await waitConnectorStatus(ConnectorID=1, expected_status="Reserved")
    assert status == "Reserved"

    # 刷一张非预约的卡


    # 刷一张预约的卡


    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 获取枪的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    # 插枪


    # 等待充电桩发送充电请求
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 获取枪的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"


@allure.feature("test_remote_start_transaction")
@pytest.mark.asyncio
async def test_remote_start_transaction(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    expiry_date = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.reserveNow(event_loop, connector_id=1, expiry_date=expiry_date,
                                        id_tag=GetCfg.get_id_tag(), reservation_id=1)
    assert response[0].status == RegistrationStatus.accepted

    # 获取枪状态
    status = await waitConnectorStatus(ConnectorID=1, expected_status="Reserved")
    assert status == "Reserved"

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

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    logging.info("插枪")
    # 插枪
    Connector.slot()

    # 等待本地发送充电请求
    flag, msg = await waitRequest("start_transaction")
    assert flag == True

    logging.info("开始充电请求为：%s" % msg)
    assert msg["id_tag"] == GetCfg.get_id_tag()
    assert msg["reservationId"] == 1

    # 判断插枪状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"


@allure.feature("test_expire")
@pytest.mark.asyncio
async def test_expire(event_loop):
    # 获取配置信息"AuthorizeRemoteTxRequests"
    result = await service.getConfiguration(event_loop, ["AuthorizeRemoteTxRequests"])
    logging.info(result)
    assert result[0]['value'] == "true"

    expiry_date = (datetime.utcnow() + timedelta(seconds=5)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.reserveNow(event_loop, connector_id=1, expiry_date=expiry_date,
                                        id_tag=GetCfg.get_id_tag(), reservation_id=1)
    assert response[0].status == RegistrationStatus.accepted

    # 获取枪状态
    status = await waitConnectorStatus(ConnectorID=1, expected_status="Reserved")
    assert status == "Reserved"

    # 等待预约过期，枪可用
    status = await waitConnectorStatus(ConnectorID=1, expected_status="Available")
    assert status == "Available"


