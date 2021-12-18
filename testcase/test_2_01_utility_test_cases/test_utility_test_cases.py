import asyncio
import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus

from connector.connector import Connector
from server import service
from server.connect import waitConnectorStatus, waitRequest, clearTriggerMessage


@allure.feature("test_revert_charge_point_to_basic_idle_state1")
@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state1(event_loop):
    # 改变配置信息"MeterValueSampleInterval"
    value = "0"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value=value)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"ClockAlignedDataInterval"
    response = await service.changeConfiguration(event_loop, key="ClockAlignedDataInterval", value=value)
    assert response[0].status == RegistrationStatus.accepted

    # 改变配置信息"LocalPreAuthorize"
    response = await service.changeConfiguration(event_loop, key="LocalPreAuthorize", value="false")
    assert response[0].status == RegistrationStatus.accepted

    # 设置桩可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    # 获取桩状态
    # status = await waitConnectorStatus(ConnectorID=0, expected_status="Available")
    # assert status == "Available"

    # 获取配置信息"AuthorizationCacheEnabled"
    result = await service.getConfiguration(event_loop, ["AuthorizationCacheEnabled"])
    assert result[0]['value'] == "true"

    # 清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"LocalAuthListEnabled"
    result = await service.getConfiguration(event_loop, ["LocalAuthListEnabled"])
    assert result[0]['value'] == "true"

    # 发送本地列表给桩 updateType=full
    with open("schema/SendLocalList.json", 'r') as f:
        data = json.load(f)
    response = await service.sendLocalList(event_loop, list_version=data.get("listVersion"),
                                           update_type=data.get("updateType"),
                                           local_authorization_list=data.get("localAuthorizationList"))
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"MaxChargingProfilesInstalled"
    result = await service.getConfiguration(event_loop, ["MaxChargingProfilesInstalled"])
    logging.info(result[0]['value'])
    if int(result[0]['value']) >= 1:
        # 清除充电配置文件
        response = await service.clearChargeProfile(event_loop, connector_id=0)
        assert response[0].status == "Accepted" or response[0].status == "Unknown"


@allure.feature("test_stop_charging_session")
@pytest.mark.asyncio
async def test_stop_charging_session(event_loop):
    # 插枪
    Connector.slot()

    # 远程启动充电
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    assert response[0].status == RegistrationStatus.accepted

    # 等待充电桩鉴权
    flag, _ = await waitRequest("authorize")
    assert flag == True

    # 等待本地开始充电
    flag, _ = await waitRequest("start_transaction")
    assert flag == True

    # 获取桩充电之后的状态
    status = await waitConnectorStatus(1, "Charging")
    assert status == "Charging"

    clearTriggerMessage()
    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted
    status = await waitConnectorStatus(1, "Preparing")
    assert status == "Preparing"
