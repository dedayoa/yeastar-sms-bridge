from userapp.tests.factories import UserFactory
from .factories import SMSMessageFactory, SMSQueueFactory
from gateway.tests.factories import DeviceFactory, SpanFactory
from pytest_factoryboy import register

register(UserFactory)
register(DeviceFactory)
register(SpanFactory)
register(SMSMessageFactory)
