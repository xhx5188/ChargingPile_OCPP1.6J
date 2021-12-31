import asyncio
import logging
import pytest
from connector.connector import Connector
from server.connect import clearTriggerMessage, waitRequest
from testcase.test_2_50_buletooth_stress.conftest import BluetoothValue


# 压力测试：蓝牙反复启停充电
@pytest.mark.asyncio
async def test_bluetooth_transaction(event_loop):
    # 插枪
    Connector.slot()

    for i in range(1000):
        logging.info("times = %s" % i)

        clearTriggerMessage()
        # 蓝牙启动充电
        flag = BluetoothValue.blue_obj.local_start_charge()
        assert flag == True

        flag, msg = await waitRequest("start_transaction", 30)
        assert flag == True
        logging.info(msg)
        assert msg["connector_id"] == 1

        flag, msg = await waitRequest("meter_values", 30)
        assert flag == True

        flag, msg = await waitRequest("meter_values", 30)
        assert flag == True

        # 蓝牙停止充电
        flag = BluetoothValue.blue_obj.local_stop_charge()
        assert flag == True
        await asyncio.sleep(30)

        flag, msg = await waitRequest("stop_transaction", 30)
        assert flag == True
        logging.info(msg)
        assert msg["reason"] == "Local"

        flag, msg = await waitRequest("heartbeat", 30)
        assert flag == True

        flag, msg = await waitRequest("heartbeat", 30)
        assert flag == True

