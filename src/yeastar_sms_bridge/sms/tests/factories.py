import factory
from phonenumber_field.phonenumber import phonenumbers
from gateway.tests.factories import SpanFactory
from userapp.tests.factories import UserFactory
from django.utils import timezone
from ..helpers import next_time

class SMSMessageFactory(factory.django.DjangoModelFactory):

    text = "This is a test message"
    recipient = phonenumbers.parse("+2348028443226")
    send_span = factory.SubFactory(SpanFactory)
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = "sms.SMSMessage"

class SMSQueueFactory(factory.django.DjangoModelFactory):

    message = factory.SubFactory(SMSMessageFactory)
    class Meta:
        model = "sms.SMSQueue"