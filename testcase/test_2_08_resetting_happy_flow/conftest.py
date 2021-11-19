import logging

import asyncio
import pytest


@pytest.fixture(scope="function")
async def connection():
    logging.info("connection start")
    await asyncio.sleep(1)
    yield 1
    logging.info("connection end")