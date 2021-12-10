import logging
import pytest
from server.connect import waitRequest


@pytest.fixture(scope="function", autouse=True)
async def waitHeartbeat(event_loop):
    yield
    logging.info("*" * 50 + "等待充电桩固件升级完成" + "*" * 50)
    flag, msg = await waitRequest("heartbeat", 350)
    logging.info(msg)
    if flag != True:
        raise Exception("charge point run failed")