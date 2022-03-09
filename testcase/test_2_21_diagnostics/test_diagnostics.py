from datetime import datetime, timedelta
import pytest
from server import service
import allure
from server.connect import waitRequest


@allure.feature("test_get_diagnostics")
@pytest.mark.asyncio
async def test_get_diagnostics(event_loop):
    # uri = "https://autel-cloud-energy-gateway-enetest.auteltech.cn/api/log-service/frontLog/acceptFrontLog"  #中国测试环境
    uri = "https://gateway-enetestuk.autel.com/api/log-service/frontLog/acceptFrontLog"  #英国测试环境

    start_time = (datetime.utcnow() - timedelta(weeks=1)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    stop_time = (datetime.utcnow() - timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.getDiagnostics(event_loop, uri, start_time=start_time, stop_time=stop_time)
    assert ".log.gz" in response[0].file_name

    flag, msg = await waitRequest("diagnostics_status_notification")
    assert flag == True
    assert msg["status"] == "Uploading"

    flag, msg = await waitRequest("diagnostics_status_notification")
    assert flag == True
    assert msg["status"] == "Uploaded"


@allure.feature("test_get_diagnostics_upload_failed")
@pytest.mark.asyncio
async def test_get_diagnostics_upload_failed(event_loop):
    uri = ""
    start_time = (datetime.utcnow() - timedelta(weeks=1)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    stop_time = (datetime.utcnow() - timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S.123Z')
    response = await service.getDiagnostics(event_loop, uri, start_time=start_time, stop_time=stop_time, retries=0)
    assert ".log.gz" in response[0].file_name

    flag, msg = await waitRequest("diagnostics_status_notification")
    assert flag == True
    assert msg["status"] == "Uploading"

    flag, msg = await waitRequest("diagnostics_status_notification")
    assert flag == True
    assert msg["status"] == "UploadFailed"