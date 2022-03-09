# --*-- encoding:utf-8 --*--
"""
@File:changeAvailability.py
@Time:2022/1/19 17:25
@Author:xionghuixin_A21772
@Copyright:Autel
"""
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import waitConnectorStatus

@allure.feature("test_SetPileState_Unavailable")
@pytest.mark.asyncio
async def test_SetPileState_Unavailable(event_loop):
    # 远程设置交流家桩的枪为不可用状态
    response = await service.changeAvailability(event_loop, connector_id=1, type="Inoperative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为不可用
    status = await waitConnectorStatus(1, "Unavailable")
    assert status == "Unavailable"

    logging.info("桩的状态设置为Unavailable成功")
