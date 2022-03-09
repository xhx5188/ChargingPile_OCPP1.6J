import logging
import pytest
from connector.connector import Connector
from server import service
from server.connect import waitRequest


@pytest.fixture(scope="function", autouse=True)
async def waitHeartbeat(event_loop):
    yield
    logging.info("*" * 50 + "等待充电桩固件升级完成" + "*" * 50)
    # 上电
    logging.info("上电")
    Connector.electricity()
    flag, msg = await waitRequest("heartbeat", 350)
    logging.info(msg)
    if flag != True:
        raise Exception("charge point run failed")

    # 桩恢复为available状态
    await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    # 枪恢复为available状态
    await service.changeAvailability(event_loop, connector_id=1, type="Operative")
