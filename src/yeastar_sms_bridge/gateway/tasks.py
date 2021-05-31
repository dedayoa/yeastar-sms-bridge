from .models import Span
from django.utils import timezone

def reset_total_messages_sent_today():
    active_spans = Span.objects.filter(sms_sending_disabled = False)
    for span in active_spans:
        user_tz = span.device.owner.profile.timezone
        if not user_tz:
            raise ValueError("User timezone needs to be set")
        date_now = timezone.now()
        user_local_date_now = timezone.localdate(date_now, timezone=user_tz)
        if not span.total_messages_sent_today_last_reset:
            span.total_messages_sent_today_last_reset = date_now
            span.save()
        user_local_total_messages_sent_today_last_reset = timezone.localdate(span.total_messages_sent_today_last_reset, timezone=user_tz)
        
        if user_local_date_now <= user_local_total_messages_sent_today_last_reset:
            continue
        span.total_messages_sent_today = 0
        span.total_messages_sent_today_last_reset = date_now
        span.save()