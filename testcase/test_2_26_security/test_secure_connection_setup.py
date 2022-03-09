import asyncio
import json
import logging
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
import allure

from server.connect import waitRequest


@allure.feature("test_update_passwd")
@pytest.mark.asyncio
async def test_update_passwd(event_loop):
    # 改变配置信息"AuthorizationKey"
    key = "OCA_OCTT_admin_test"
    response = await service.changeConfiguration(event_loop, key="AuthorizationKey", value=key.encode().hex().upper())
    assert response[0].status == RegistrationStatus.accepted
    await asyncio.sleep(60)


@allure.feature("test_update_certificate")
@pytest.mark.asyncio
async def test_update_certificate(event_loop):
    # 改变配置信息"CpoName"
    response = await service.changeConfiguration(event_loop, key="CpoName", value="Autel")
    assert response[0].status == RegistrationStatus.accepted

    # 使充电桩发送签名证书请求
    response = await service.extendedTriggerMessage(event_loop, requested_message="SignChargePointCertificate")
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地发送签名证书请求
    flag, msg = await waitRequest("sign_certificate")
    logging.info("msg=%s" % msg)
    assert flag == True

    # 服务端发送签名证书
    response = await service.certificateSigned(event_loop, "")
    logging.info("response=%s" % response)
    assert response[0].status == RegistrationStatus.accepted

    # 等待本地重连（使用新的证书）。。。
