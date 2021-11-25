import asyncio
import json
import logging
import time
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import Value, clearTriggerMessage, waitConnectorStatus, waitRequest


@pytest.mark.asyncio
async def test_get_local_list_version_not_supported(event_loop):
    # 改变配置信息"LocalAuthListEnabled"
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="True")
    assert response[0].status == "Accepted"

    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList1.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # 发送本地列表给桩 updateType=differential
    with open("schema/SendLocalList2.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted
