import pytest
from sms.models import SMSQueue
from ..helpers import yeastar_sms_send, parse_response_from_gateway, requests
from ..models import Span

@pytest.mark.django_db
def test_yeastar_sms_send(mocker, queued_message, settings):
    mock_request = mocker.patch.object(requests, 'get', autospec=True)
    sms_message = queued_message.message
    span = sms_message.send_span
    payload = {
        'account': span.device.api_username,
        'password': span.device.api_password,
        'port': span.port_id(),
        'destination': str(sms_message.recipient),
        'content': str(sms_message.text)
    }
    yeastar_sms_send(queued_message)
    mock_request.assert_called_with(
        url = span.device.api_url,
        params = payload,
        timeout = settings.MAX_GATEWAY_HTTP_TIMEOUT
    )

@pytest.mark.django_db
def test_yeastar_sms_send_success(mocker, queued_message, span):
    mock_parsed_response = mocker.patch("gateway.helpers.parse_response_from_gateway")
    mock_parsed_response.return_value = "success"
    mock_request = mocker.patch.object(requests, 'get', autospec=True)
    mock_request.return_value.status_code = 200
    yeastar_sms_send(queued_message)
    assert Span.objects.get(id = span.id).total_messages_sent == queued_message.message.pages
    assert not SMSQueue.objects.filter(id = queued_message.id).exists()



@pytest.mark.parametrize(
    "response, result",
    [
        ("""
Response: Failed
Message: Commit failed!
        """, "failed"),
        ("""
Response: Success
Message: Commit successfully!
        """, "success"),
        ("ajdfjn", None),
        ("", None),
        ("""
Response: Error
Message: The port(3) is not active!
        """, "error")
    ]
)
def test_parse_response_from_gateway(response, result):
    assert parse_response_from_gateway(response) == result
