from .models import SMSMessage, SMSQueue
from gateway.helpers import get_span_by_profile

def queue_messages():
    new_messages = SMSMessage.objects.filter(status = SMSMessage.Status.NEW)
    for message in new_messages:
        SMSQueue.objects.create(
            message = message,
            send_span = get_span_by_profile(user_id=message.owner.id)
        )