# --*-- encoding:utf-8 --*--
"""
@File:test_1.py
@Time:2022/1/23 12:41
@Author:xionghuixin_A21772
@Copyright:Autel
"""
import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest
from time import sleep


# 压力测试：远程反复启停充电
@allure.feature("test_Recurrent_cpVoltN")
@pytest.mark.asyncio
async def test_Recurrent_cpVoltN(event_loop):
    # 插枪
    Connector.slot()

    # 获取交流家桩的枪启动充电之前的状态
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"

    for i in range(500):
        logging.info("========这是第%s次开始执行========" % str(i+1))
        # 远程启动充电
        clearTriggerMessage()
        with open("schema/RemoteStartTransaction.json", 'r') as f:
            data = json.load(f)
        response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                        connector_id=data.get('connectorId'),
                                                        charging_profile=data.get('chargingProfile'))
        assert response[0].status == RegistrationStatus.accepted

        # 等待鉴权通过
        flag, _ = await waitRequest("authorize", 30)
        assert flag is True

        # 等待桩返回开始订单的信息
        flag, _ = await waitRequest("start_transaction")
        assert flag is True

        # 获取桩充电之后的状态
        status = await waitConnectorStatus(1, "Charging", 30)
        assert status == "Charging"
        logging.info("********正在充电********稍等约1分钟********")
        # sleep(50)

        # 结束远程充电
        response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
        assert response[0].status == RegistrationStatus.accepted
        status = await waitConnectorStatus(1, "Preparing", 30)
        assert status == "Preparing"

        # 重启充电桩
        clearTriggerMessage()
        response = await service.reset(event_loop, "Soft")
        assert response[0].status == RegistrationStatus.accepted
        logging.info("稍等，桩正在重启")
        # sleep(20)

        # 等待充电桩重启
        flag, _ = await waitRequest("boot_notification")
        assert flag is True
        # logging.info("稍等5秒，等桩连上后台")
        # sleep(5)

        # 等待桩状态为可用
        status = await waitConnectorStatus(0, "Available")
        assert status == "Available"
        status = await waitConnectorStatus(1, "Preparing")
        assert status == "Preparing"
