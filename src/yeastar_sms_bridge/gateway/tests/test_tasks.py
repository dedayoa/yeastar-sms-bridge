import datetime

import pytest
from pytz import UTC

from ..models import Span
from ..tasks import reset_total_messages_sent_today


@pytest.mark.django_db
def test_reset_total_messages_sent_today(mocker, user_profile, span_factory):
    dt_now = datetime.datetime(2020, 12, 10, 13, 12, 11, 0, tzinfo=UTC)
    mock_now = mocker.patch("gateway.tasks.timezone.now")
    mock_now.return_value = dt_now
    span = span_factory(total_messages_sent_today = 132, total_messages_sent_today_last_reset = dt_now - datetime.timedelta(days=1))
    reset_total_messages_sent_today()
    new_span = Span.objects.get(id = span.id)
    assert new_span.total_messages_sent_today == 0
    assert new_span.total_messages_sent_today_last_reset == dt_now
