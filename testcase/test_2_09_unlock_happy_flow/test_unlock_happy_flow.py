import json
import logging

import pytest
from ocpp.v16.enums import RegistrationStatus

from server import service
from server.connect import Value, clearTriggerMessage, waitConnectorStatus, waitRequest


@pytest.mark.asyncio
async def test_unlock_connector_no_charging_session(event_loop):
    flag = await waitRequest("boot_notification", 100)
    assert flag == True