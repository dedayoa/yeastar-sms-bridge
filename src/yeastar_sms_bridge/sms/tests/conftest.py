import pytest
from django.utils import timezone
from gateway.tests.factories import (DeviceFactory, SendProfileFactory,
                                     SpanFactory)
from pytest_factoryboy import register
from userapp.tests.factories import UserFactory

from .factories import SMSMessageFactory, SMSQueueFactory, SMSMessageStateLogFactory

register(UserFactory)
register(DeviceFactory)
register(SpanFactory)

@pytest.fixture
def send_profile_1(span, user):
    return SendProfileFactory(spans=(span,), user=user)

register(SMSMessageFactory)
register(SMSQueueFactory)
register(SMSMessageStateLogFactory)
