from ..helpers import next_time, backoff_with_jitter
from django.utils import timezone
import pytest
from datetime import datetime
from pytz.reference import UTC



def test_backoff_with_jitter():
    pass


@pytest.mark.parametrize(
    "dt_time, attempt, backoff, result", [
        (datetime(2020, 10,10,10,0,0,0, tzinfo=UTC), 0, 3600, datetime(2020,10,10,11,0,0,0, tzinfo=UTC)),
        (datetime(2020, 10,10,10,0,0,0, tzinfo=UTC), 1, 600, datetime(2020,10,10,10,10,0,0, tzinfo=UTC)),
    ]
)
def test_next_time(mocker, dt_time, attempt, backoff, result):
    mock_backoff = mocker.patch('sms.helpers.backoff_with_jitter')
    mock_backoff.return_value = backoff
    assert next_time(dt_time, attempt) == result