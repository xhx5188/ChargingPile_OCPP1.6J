import asyncio
import logging
from bluetooth.bluetooth import Buletooth
import pytest


# @pytest.fixture(scope="function")
# async def buletooth():
#     logging.info("*" * 50 + "bluetooth connect" + "*" * 50)
#     blue_obj = Buletooth()
#     flag = blue_obj.connect_bluetooth_server()
#     if flag != True:
#         raise Exception("connect to the bluetooth failed and testcase is fail")
#     logging.info("*" * 50 + "bluetooth connect ok" + "*" * 50)
#     yield blue_obj
#     logging.info("*" * 50 + "bluetooth disconnect" + "*" * 50)
#     blue_obj.disconnect_bluetooth_server()
#     await asyncio.sleep(60)
