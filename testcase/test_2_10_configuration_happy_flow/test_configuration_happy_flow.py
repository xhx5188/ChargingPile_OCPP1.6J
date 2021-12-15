import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure


@allure.feature("test_retrieve_configuration")
@pytest.mark.asyncio
async def test_retrieve_configuration(event_loop):
    # 获取配置信息"SupportedFeatureProfiles"
    result = await service.getConfiguration(event_loop, ["SupportedFeatureProfiles"])
    logging.info(result)
    assert result[0]['value'] == "Core,FirmwareManagement,LocalAuthListManagement,SmartCharging,RemoteTrigger"

    #
    result = await service.getConfiguration(event_loop)
    logging.info(result)
    config = {}
    for d in result:
        config[d['key']] = d['readonly']
    logging.info(config)

    #Core
    assert config.get("AuthorizeRemoteTxRequests") == True
    assert config.get("ClockAlignedDataInterval") == False
    assert config.get("ConnectionTimeOut") == False
    assert config.get("ConnectorPhaseRotation") == False
    assert config.get("GetConfigurationMaxKeys") == True
    assert config.get("HeartbeatInterval") == False
    assert config.get("LocalAuthorizeOffline") == False
    assert config.get("MeterValuesAlignedData") == False
    assert config.get("MeterValuesSampledData") == False
    assert config.get("MeterValueSampleInterval") == False
    assert config.get("NumberOfConnectors") == True
    assert config.get("ResetRetries") == False
    assert config.get("StopTransactionOnInvalidId") == False
    assert config.get("StopTxnAlignedData") == False
    assert config.get("StopTxnSampledData") == False
    assert config.get("SupportedFeatureProfiles") == True
    assert config.get("TransactionMessageAttempts") == False
    assert config.get("TransactionMessageRetryInterval") == False
    assert config.get("UnlockConnectorOnEVSideDisconnect") == False

    #Local Auth List Management
    assert config.get("LocalAuthListEnabled") == False
    assert config.get("LocalAuthListMaxLength") == True
    assert config.get("SendLocalListMaxLength") == True

    #Smart Charging Profile
    assert config.get("ChargeProfileMaxStackLevel") == True
    assert config.get("ChargingScheduleAllowedChargingRateUnit") == True
    assert config.get("ChargingScheduleMaxPeriods") == True
    assert config.get("MaxChargingProfilesInstalled") == True

    # 获取配置信息"GetConfigurationMaxKeys"
    result = await service.getConfiguration(event_loop, ["GetConfigurationMaxKeys"])
    logging.info(result)
    cfg_max = int(result[0]['value'])

    get_config_list = ["AuthorizeRemoteTxRequests", "ClockAlignedDataInterval", "ConnectionTimeOut",
                       "ConnectorPhaseRotation", "GetConfigurationMaxKeys", "HeartbeatInterval",
                       "LocalAuthorizeOffline", "MeterValuesAlignedData", "MeterValuesSampledData",
                       "MeterValueSampleInterval", "NumberOfConnectors", "ResetRetries",
                       "StopTransactionOnInvalidId", "StopTxnAlignedData", "StopTxnSampledData",
                        "SupportedFeatureProfiles", "TransactionMessageAttempts", "TransactionMessageRetryInterval",
                        "UnlockConnectorOnEVSideDisconnect"]

    # 获取配置信息
    result = await service.getConfiguration(event_loop, get_config_list)
    logging.info(result)
    assert len(result) <= cfg_max


@allure.feature("test_change_set_configuration")
@pytest.mark.asyncio
async def test_change_set_configuration(event_loop):
    # 改变配置信息"MeterValueSampleInterval"
    response = await service.changeConfiguration(event_loop, key="MeterValueSampleInterval", value="3")
    assert response[0].status == RegistrationStatus.accepted


    # 获取配置信息"MeterValueSampleInterval"
    result = await service.getConfiguration(event_loop, ["MeterValueSampleInterval"])
    logging.info(result)
    assert result[0]['value'] == "3"



