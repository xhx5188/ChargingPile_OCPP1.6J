import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure


@allure.feature("test_download_and_install")
@pytest.mark.asyncio
async def test_download_and_install(event_loop):
    service.updateFirmware(event_loop, )