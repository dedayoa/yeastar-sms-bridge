import pytest

@pytest.mark.django_db
class TestSpan:
    
    def test_string_representation(self, span):
        assert str(span) == f"Channel: {span.channel_id}, {span.SIM_phone_number}"

    def test_port_id(self, span):
        assert span.port_id() == int(span.channel_id) - 1



@pytest.mark.django_db
class TestDevice:
    
    def test_string_representation(self, device):
        assert str(device) == f"{device.name}/{device.owner}"

@pytest.mark.django_db
class TestSendProfile:

    def test_string_representation(self, send_profile):
        assert str(send_profile) == send_profile.name