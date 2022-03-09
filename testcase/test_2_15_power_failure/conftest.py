import asyncio
import pytest
from connector.connector import Connector


@pytest.fixture(scope="function", autouse=True)
async def power(event_loop):
    yield
    Connector.electricity()
    await asyncio.sleep(30)
