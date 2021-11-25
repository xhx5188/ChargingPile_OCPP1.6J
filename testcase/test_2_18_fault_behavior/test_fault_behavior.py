import asyncio
import pytest
from server.connect import waitConnectorStatus, waitRequest


@pytest.mark.asyncio
async def test_fault_behavior(event_loop):
    # 将充电桩设为错误状态。。。

    # 等待充电桩状态
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Faulted")
    assert status == "Faulted"
    await asyncio.sleep(20)


    # 本地尝试启动充电。。。


    # 本地启动充电失败
    flag, _ = await waitRequest("start_transaction")
    assert flag == False