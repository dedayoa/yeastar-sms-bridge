import pytest
from pytz.reference import UTC

from gateway.tests.factories import DeviceFactory, SpanFactory, SendProfileFactory
from userapp.tests.factories import UserFactory, UserProfileFactory
from pytest_factoryboy import register
from sms.tests.factories import SMSQueueFactory, SMSMessageFactory
import datetime

register(UserFactory)
register(UserProfileFactory)
register(DeviceFactory)
register(SpanFactory)
register(SendProfileFactory)

register(SMSMessageFactory)
register(SMSQueueFactory, 'queued_message', next_submit_attempt_at = datetime.datetime(2020, 10, 10, 10, 11, 22, 0, tzinfo=UTC))