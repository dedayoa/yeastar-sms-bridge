import factory
from phonenumber_field import phonenumber
from userapp.tests.factories import UserFactory
from ..models import SendProfile

class DeviceFactory(factory.django.DjangoModelFactory):

    name = "TG400"
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = 'gateway.Device'

class SpanFactory(factory.django.DjangoModelFactory):
    channel_id = 1
    SIM_phone_number = phonenumber.phonenumbers.parse("+2348028443225")
    device = factory.SubFactory(DeviceFactory)
    name = factory.Sequence(lambda n: f"Span #{n}")

    class Meta:
        model = 'gateway.Span'

class SendProfileFactory(factory.django.DjangoModelFactory):

    name = "Port 3 only"
    strategy = SendProfile.SendStrategy.SINGLE
    user = factory.SubFactory(UserFactory)
    
    @factory.post_generation
    def spans(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for span in extracted:
                self.spans.add(span)

    class Meta:
        model = 'gateway.SendProfile'