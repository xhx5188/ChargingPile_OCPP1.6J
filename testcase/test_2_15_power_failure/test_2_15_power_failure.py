import asyncio
import json
import logging
import time
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus, waitRequest

@pytest.mark.asyncio
async def test_11(event_loop):
    logging.info("wait.....")
    await asyncio.sleep(360000)