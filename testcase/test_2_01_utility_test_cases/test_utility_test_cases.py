import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import clearTriggerMessage, waitConnectorStatus


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


@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state2(event_loop):
    #设置桩可用
    response = await service.changeAvailability(event_loop, connector_id=0, type="Operative")
    assert response[0].status == RegistrationStatus.accepted

    #获取桩状态
    status = await waitConnectorStatus(ConnectorID=0, expected_status="Available")
    assert status == "Available"

    # 获取配置信息"AuthorizationCacheEnabled"
    result = await service.getConfiguration(event_loop, ["AuthorizationCacheEnabled"])
    assert result[0]['value'] == "true"

@pytest.mark.asyncio
async def test_revert_charge_point_to_basic_idle_state3(event_loop):
    #清除缓存
    response = await service.clearCache(event_loop)
    assert response[0].status == RegistrationStatus.accepted

    # 获取配置信息"LocalAuthListEnabled"
    result = await service.getConfiguration(event_loop, ["LocalAuthListEnabled"])
    assert result[0]['value'] == "true"

    # 获取配置信息"MaxChargingProfilesInstalled"
    result = await service.getConfiguration(event_loop, ["MaxChargingProfilesInstalled"])
    logging.info(result[0]['value'])
    if result[0]['value'] != "0":
        #清除充电配置文件
        response = await service.clearChargeProfile(event_loop, connector_id=0)
        assert response[0].status == RegistrationStatus.accepted
