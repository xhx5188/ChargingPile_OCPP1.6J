import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure


@allure.feature("test_send_local_authorization_list1")
@pytest.mark.asyncio
async def test_send_local_authorization_list1(event_loop):
    # 改变配置信息"LocalAuthListEnabled"
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="true")
    assert response[0].status == "Accepted"

    # 发送本地列表给桩 updateType=Differential
    with open("schema/SendLocalList2.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩的本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")

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
    assert response[0].list_version == data.get("listVersion")


@allure.feature("test_send_local_authorization_list2")
@pytest.mark.asyncio
async def test_send_local_authorization_list2(event_loop):
    # 改变配置信息"LocalAuthListEnabled"
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="false")
    assert response[0].status == "Accepted"

    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList1.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == "NotSupported"


@allure.feature("test_send_local_authorization_list3")
@pytest.mark.asyncio
async def test_send_local_authorization_list3(event_loop):
    # 改变配置信息"LocalAuthListEnabled"
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="true")
    assert response[0].status == "Accepted"

    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList3_1.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩的本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")


    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList3_2.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩的本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)
    assert response[0].list_version == data.get("listVersion")
    version = data.get("listVersion")

    # 发送本地列表给桩 updateType=Differential
    with open("schema/SendLocalList3_3.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == "VersionMismatch"

    # 获取桩的本地列表版本
    response = await service.getLocalListVersion(event_loop)
    logging.info(response)
    assert response[0].list_version == version


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
    assert response[0].list_version == data.get("listVersion")


@pytest.mark.skip("需要模拟故障")
@allure.feature("test_send_local_authorization_list4")
@pytest.mark.asyncio
async def test_send_local_authorization_list4(event_loop):
    # 改变配置信息"LocalAuthListEnabled"
    response = await service.changeConfiguration(event_loop, key="LocalAuthListEnabled", value="true")
    assert response[0].status == "Accepted"

    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList1.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == "Failed"