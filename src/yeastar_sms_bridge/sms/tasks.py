from .models import SMSMessage, SMSQueue, SMSMessageStateLog
from gateway.helpers import get_span_by_profile
from gateway.helpers import yeastar_sms_send
from django.conf import settings
from django.utils import timezone
import logging
from .helpers import next_time


logger = logging.getLogger(__name__)

def queue_messages():
    now = timezone.now()
    new_messages = SMSMessage.objects.filter(status = SMSMessage.Status.NEW)
    for message in new_messages:
        SMSQueue.objects.create(
            message = message,
            next_submit_attempt_at = next_time(now, 0)
        )
        message.send_span = get_span_by_profile(user_id=message.owner.id)
        message.status = SMSMessage.Status.QUEUED
        message.save()

def process_queued_messages():
    max_sms_to_get = settings.MAX_SMS_BATCH_REQUEST
    if max_sms_to_get < 1:
        max_sms_to_get = 1

    max_submit_attempts = settings.MAX_SUBMIT_ATTEMPTS
    if max_submit_attempts < 1:
        max_submit_attempts = 1

    for smsq in SMSQueue.objects.filter(message__status = SMSMessage.Status.SUCCESS):
        smsq.delete()

    for smsq in SMSQueue.objects.filter(submit_attempts__gte = max_submit_attempts):
        smsq.message.add_state_log(SMSMessageStateLog.State.FAILED, "Maximum submit tries attempted")
        smsq.delete()

    sms_messages = SMSQueue.objects.filter(next_submit_attempt_at__lte = timezone.now())[0:max_sms_to_get]

    for smsq in sms_messages:
        
        if smsq.message.send_span.sms_sending_disabled or smsq.message.send_span.device.sms_sending_disabled:
            logger.info("SMS sending disabled")
            continue
        
        smsq.message.add_state_log(SMSMessageStateLog.State.PROCESSING)
        yeastar_sms_send(smsq)
        smsq.submit_attempts += 1
        smsq.next_submit_attempt_at = next_time(timezone.now(), smsq.submit_attempts)
        smsq.save()