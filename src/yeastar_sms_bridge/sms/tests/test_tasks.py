import pytest

from sms.helpers import next_time
from ..tasks import queue_messages, process_queued_messages
from ..models import SMSQueue, SMSMessage
from datetime import datetime, timedelta
from pytz.reference import UTC

@pytest.mark.django_db
def test_queue_messages(mocker, sms_message, send_profile_1):
    dt_time = datetime(2020, 10, 10, 10, 10, 0, 0, tzinfo=UTC)
    mock_timezone_now = mocker.patch('django.utils.timezone.now')
    mock_timezone_now.return_value = dt_time
    queue_messages()
    assert SMSQueue.objects.filter(message = sms_message, created=dt_time).exists()
    assert SMSMessage.objects.get(id = sms_message.id).status == SMSMessage.Status.QUEUED

@pytest.mark.parametrize(
    "max_submit_attempts, attempts, result", [
        (2, 2, False),
        (2, 5, False),
        (2, 1, True),
        (-3, 0, True),
        (-3, 1, False),
    ]
)
@pytest.mark.django_db
def test_process_queued_messages_attempts_over_under_max_attempts(settings, sms_message, max_submit_attempts, attempts, result, sms_queue_factory):
    settings.MAX_SUBMIT_ATTEMPTS = max_submit_attempts
    sms_queue_factory(submit_attempts = attempts, message = sms_message)
    process_queued_messages()
    assert SMSQueue.objects.filter(message = sms_message).exists() == result

@pytest.mark.django_db
def test_process_queued_messages_success_message_is_deleted(mocker, sms_message_factory, sms_queue_factory):
    dt_time = datetime(2020, 10, 10, 10, 11, 0, 0, tzinfo=UTC)
    mock_timezone_now = mocker.patch('django.utils.timezone.now')
    mock_timezone_now.return_value = dt_time
    sms_message = sms_message_factory(status = SMSMessage.Status.SUCCESS)
    sms_queue_factory(message = sms_message, submit_attempts = 1, next_submit_attempt_at = dt_time - timedelta(seconds = 55))
    process_queued_messages()
    assert not SMSQueue.objects.filter(message = sms_message).exists()

@pytest.mark.django_db
def test_process_queued_messages(mocker, sms_queue_factory, sms_message):
    dt_time = datetime(2020, 10, 10, 10, 11, 0, 0, tzinfo=UTC)
    dt_time_next = datetime(2020, 10, 10, 10, 11, 14, tzinfo=UTC)
    
    mock_yeastar_send_sms = mocker.patch('sms.tasks.yeastar_sms_send')
    mock_timezone_now = mocker.patch('django.utils.timezone.now')
    mock_timezone_now.return_value = dt_time
    mock_next_time = mocker.patch('sms.tasks.next_time')
    mock_next_time.return_value = dt_time_next

    sms_queue_factory(next_submit_attempt_at = datetime(2020, 10, 10, 10, 10, 0, 0, tzinfo=UTC), message = sms_message)
    process_queued_messages()
    mock_yeastar_send_sms.assert_called()
    assert SMSQueue.objects.filter(message = sms_message, submit_attempts = 1, next_submit_attempt_at = dt_time_next).exists()

