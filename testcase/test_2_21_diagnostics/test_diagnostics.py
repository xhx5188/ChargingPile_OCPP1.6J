import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure


@allure.feature("test_get_diagnostics")
@pytest.mark.asyncio
async def test_get_diagnostics(event_loop):
    service.getDiagnostics()