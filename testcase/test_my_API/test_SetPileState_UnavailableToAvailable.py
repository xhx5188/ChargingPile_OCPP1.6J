# --*-- encoding:utf-8 --*--
"""
@File:test_SetPileState_UnavailableToAvailable.py
@Time:2022/1/20 15:51
@Author:xionghuixin_A21772
@Copyright:Autel
"""
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import waitConnectorStatus
import allure

@allure.feature("test_SetPileState_UnavailableToAvailable")
@pytest.mark.asyncio
async def test_SetPileState_UnavailableToAvailable(event_loop):

    # 远程设置桩为可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 等待桩状态为可用
    status = await waitConnectorStatus(0, "Available")
    assert status == "Available"
    status = await waitConnectorStatus(1, "Available")
    assert status == "Available"

    logging.info("桩的状态设置为Available成功")
