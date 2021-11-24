import json
import logging
import time
from datetime import datetime, timedelta

import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest

@pytest.mark.asyncio
async def test_local_start_transaction(event_loop):
    expiry_date = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.reserveNow(event_loop, connector_id=1, expiry_date=expiry_date,
                                        id_tag="AE0022A1GM9C00041C", reservation_id=1)
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