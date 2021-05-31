import pytest

# Create your tests here.
@pytest.mark.django_db
class TestSMSMessage:

    def test_string_representation(self, sms_message):
        assert str(sms_message) == sms_message.text