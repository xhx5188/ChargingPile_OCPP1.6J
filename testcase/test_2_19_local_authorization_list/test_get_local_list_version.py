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
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="False")
    assert response[0].status == "Accepted"

    response = await service.getLocalListVersion(event_loop)
    # -1: 无活跃的本地认证列表
    assert response[0].list_version == -1


@pytest.mark.asyncio
async def test_get_local_list_version_empty(event_loop):
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

    # 获取桩的本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

    # 清空本地列表
    with open("./schema/clearLocalList.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # 获取本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)
    assert response[0].list_version == 0