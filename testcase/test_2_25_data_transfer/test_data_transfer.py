import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure


@allure.feature("test_data_transfer_to_charge_point")
@pytest.mark.asyncio
async def test_data_transfer_to_charge_point(event_loop):
    response = await service.dataTransfer(event_loop, "AUTEL")
    logging.info(response)
    assert response[0].status == RegistrationStatus.rejected or response[0].status == "UnknownVendorId"


@pytest.mark.skip(reason="场景构造待确认")
@allure.feature("test_data_transfer_to_charge_point")
@pytest.mark.asyncio
async def test_data_transfer_to_central_system(event_loop):
    pass