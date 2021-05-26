from .models import SMSMessage, SMSQueue

def queue_messages():
    sms_to_queue = SMSMessage.objects.filter(submitted_ok = False, failed = False)
    