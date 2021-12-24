import asyncio
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from connector.connector import Connector
from server import service
from server.connect import waitConnectorStatus, waitRequest, clearTriggerMessage

@pytest.mark.skip("需要支持一桩多枪")
@allure.feature("one_reader_for_multiple_connectors")
@pytest.mark.asyncio
async def one_reader_for_multiple_connectors(event_loop):
    pass