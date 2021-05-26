import pytest

from gateway.tests.factories import DeviceFactory, SpanFactory, SendProfileFactory
from userapp.tests.factories import UserFactory
from pytest_factoryboy import register

register(UserFactory)
register(DeviceFactory)
register(SpanFactory)
register(SendProfileFactory)