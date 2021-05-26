from .models import SMSQueue, SMSMessageStateLog
from gateway.helpers import yeastar_sms_send
from django.conf import settings
from django.utils import timezone
import logging
import random

from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

base = 10
cap = 2*24*3600 # 2 days


def backoff_with_jitter(attempt):
    return random.randrange(min(cap, (base-5) * 2 ** attempt), min(cap, base * 2 ** attempt))

def next_time(cur_time: datetime, attempt: int) -> datetime:
    return cur_time + timedelta(seconds = backoff_with_jitter(attempt))

def process_queued_messages():
    max_sms_to_get = settings.MAX_SMS_BATCH_REQUEST
    if max_sms_to_get < 1:
        max_sms_to_get = 1

    max_submit_attempts = settings.MAX_SUBMIT_ATTEMPTS
    if max_submit_attempts < 1:
        max_submit_attempts = 1

    for smsq in SMSQueue.objects.filter(submit_attempts__gte = max_submit_attempts):
        smsq.message.add_state_log(SMSMessageStateLog.State.FAILED, "Maximum submit tries attempted")
        smsq.delete()

    sms_messages = SMSQueue.objects.filter(next_submit_attempt_at__lte = timezone.now())[0:max_sms_to_get]

    for smsq in sms_messages:
        
        if smsq.send_span.sms_sending_disabled or smsq.send_span.device.sms_sending_disabled:
            logger.info("SMS sending disabled")
            continue
        
        smsq.message.add_state_log(SMSMessageStateLog.State.PROCESSING)
        yeastar_sms_send(smsq)
        smsq.submit_attempts += 1
        smsq.next_submit_attempt_at = next_time(timezone.now(), smsq.submit_attempts)
        smsq.save()