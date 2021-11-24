import json
import logging
import time
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest

@pytest.mark.asyncio
async def test_unlock_failure(event_loop):
    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=1)
    assert response[0].status == "UnlockFailed"


@pytest.mark.asyncio
async def test_unknown_connector(event_loop):
    # 解锁枪
    response = await service.unlockConnector(event_loop, connector_id=2)
    assert response[0].status == "NotSupported"