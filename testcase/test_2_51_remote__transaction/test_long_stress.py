import asyncio
import json
import logging

import allure
import pytest
from ocpp.v16.enums import RegistrationStatus

from bluetooth.bluetooth import Buletooth
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest, Value


# 压力测试：远程反复启停充电
@allure.feature("test_transaction_stress")
@pytest.mark.need_long_time
@pytest.mark.asyncio
async def test_transaction_stress(event_loop):
    # 插枪
    Connector.slot()

    # 获取桩充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    with open("../schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
        for i in range(500):
            logging.info("times = %s" % i)
            # 远程启动充电
            clearTriggerMessage()
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



@pytest.mark.asyncio
@allure.feature("test_get_config")
async def test_get_config(event_loop):
    await service.getConfiguration(event_loop, ["ClockAlignedDataInterval"])
    await asyncio.sleep(36000)

@pytest.mark.asyncio
@allure.feature("test_unplug_in_transaction")
async def test_get_config(event_loop):
    # 插枪
    Connector.slot()

    with open("../schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    
    # 远程启动充电
    clearTriggerMessage()
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

    # 拔枪
    logging.info("拔枪")
    Connector.unslot()

    await asyncio.sleep(10)

    # 重新插枪
    logging.info("重新插枪")
    Connector.slot()

    await asyncio.sleep(50)

    #
