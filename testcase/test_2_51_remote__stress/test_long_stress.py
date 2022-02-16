import asyncio
import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus

from bluetooth.bluetooth import Buletooth
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest, Value


# 压力测试：远程反复启停充电
@pytest.mark.need_long_time
@pytest.mark.asyncio
async def test_transaction_stress(event_loop):
    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    for i in range(100):
        logging.info("times = %s" % i)
        # 远程启动充电
        clearTriggerMessage()
        with open("../schema/RemoteStartTransaction.json", 'r') as f:
            data = json.load(f)
        response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                        connector_id=data.get('connectorId'),
                                                        charging_profile=data.get('chargingProfile'))
        assert response[0].status == RegistrationStatus.accepted

        # 等待充电桩鉴权
        flag, _ = await waitRequest("authorize", 30)
        assert flag == True

        # 获取桩充电之后的状态
        status = await waitConnectorStatus(1, "Charging", 30)
        assert status == "Charging"

        flag, msg = await waitRequest("meter_values", 30)
        assert flag == True
        assert msg['transaction_id'] == 1

        flag, msg = await waitRequest("meter_values", 30)
        assert flag == True
        assert msg['transaction_id'] == 1

        flag, msg = await waitRequest("meter_values", 30)
        assert flag == True
        assert msg['transaction_id'] == 1

        # 结束远程充电
        response = await service.remoteStopTransaction(event_loop, Value.transactionId_1)
        assert response[0].status == RegistrationStatus.accepted
        status = await waitConnectorStatus(1, "Preparing", 30)
        assert status == "Preparing"

