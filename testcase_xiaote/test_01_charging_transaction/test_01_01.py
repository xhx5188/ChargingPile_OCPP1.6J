import asyncio
import json
import logging
import allure
import pytest
from ocpp.v16.enums import RegistrationStatus
from server import service
from server.connect import waitConnectorStatus, waitRequest


@allure.feature("test_charging")
@pytest.mark.asyncio
async def test_charging(event_loop):
    # 远程启动充电
    with open("schema/RemoteStartTransaction.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'))
    logging.info(response)
    assert response[0].status == RegistrationStatus.accepted

    status = await waitConnectorStatus(2, "Charging", 30)
    assert status == "Charging"

    seconds = 20
    logging.info("充电等待%s秒" % seconds)
    await asyncio.sleep(seconds)
    logging.info("结束等待")

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    status = await waitConnectorStatus(2, "Preparing", 30)
    assert status == "Preparing"

    # 等待充电桩发送订单信息
    flag, msg = await waitRequest("data_transfer")
    logging.info(msg)
    assert flag == True

    await asyncio.sleep(10)


# 下发的模板个数等于预期
@allure.feature("test_bill_template1")
@pytest.mark.asyncio
async def test_bill_template1(event_loop):
    with open("schema/BillTemplate.json", 'r') as f:
        data = json.load(f)
    response = await service.dataTransfer(event_loop, vendor_id=data.get('vendorId'), \
                                          message_id=data.get('messageId'), data=data.get('data'))
    logging.info(response[0])
    assert response[0].status == "Accepted"
    # status = Accepted Rejected UnknownMessageId UnknownVendorId     data_transfer


# 下发的模板个数小于于预期
@allure.feature("test_bill_template2")
@pytest.mark.asyncio
async def test_bill_template2(event_loop):
    with open("schema/BillTemplateLessNum.json", 'r') as f:
        data = json.load(f)
    response = await service.dataTransfer(event_loop, vendor_id=data.get('vendorId'), \
                                          message_id=data.get('messageId'), data=data.get('data'))
    logging.info(response[0])
    assert response[0].status == "Accepted"


# 下发的模板个数大于预期
@allure.feature("test_bill_template3")
@pytest.mark.asyncio
async def test_bill_template3(event_loop):
    with open("schema/BillTemplateMoreNum.json", 'r') as f:
        data = json.load(f)
    response = await service.dataTransfer(event_loop, vendor_id=data.get('vendorId'), \
                                          message_id=data.get('messageId'), data=data.get('data'))
    logging.info(response[0])
    assert response[0].status == "Accepted"


@allure.feature("test_charging_with_bill")
@pytest.mark.asyncio
async def test_charging_with_bill(event_loop):
    # 远程启动充电
    with open("schema/ChargingWithBill.json", 'r') as f:
        data = json.load(f)
    response = await service.remoteStartTransaction(event_loop, id_tag=data.get('idTag'),
                                                    connector_id=data.get('connectorId'),
                                                    charging_profile=data.get('chargingProfile'),
                                                    balance=data.get("balance"),
                                                    bill_template_id=data.get('billTemplateId'))
    assert response[0].status == RegistrationStatus.accepted

    status = await waitConnectorStatus(2, "Charging", 30)
    assert status == "Charging"

    seconds = 120
    logging.info("开始充电")
    await asyncio.sleep(seconds)
    logging.info("结束充电")

    # 结束远程充电
    response = await service.remoteStopTransaction(event_loop, data['chargingProfile']['transactionId'])
    assert response[0].status == RegistrationStatus.accepted

    status = await waitConnectorStatus(2, "Preparing")
    assert status == "Preparing"

    response = await waitRequest("data_transfer")
    logging.info(response)
    logging.info(response[0])
    assert response[0].vendorId == "Autel"
    # assert response[0].messageId == "BIllUpload"  #Billtemplate