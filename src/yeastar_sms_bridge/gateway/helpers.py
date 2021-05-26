import requests
from django.conf import settings
from gateway.models import Span

from sms.models import SMSMessage, SMSMessageStateLog
from requests.exceptions import ConnectionError

def yeastar_sms_send(queued_message):
    
    message = queued_message.message
    span = queued_message.send_span

    url = span.device.api_url
    
    payload = {
        'account': span.device.api_username,
        'password': span.device.api_password,
        'port': span.port_id(),
        'destination': str(message.recipient),
        'content': str(message.text)
    }
    message_obj = SMSMessage.objects.get(id = message.id)
    span_obj = Span.objects.get(id = span.id)
    try:
        r = requests.get(url, params=payload, timeout = settings.MAX_GATEWAY_HTTP_TIMEOUT)
        if r.status_code > 299:
            message_obj.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Gateway returned {r.status_code} http code")
            span_obj.message_failure_count += 1

        rd = dict(item.split(":") for item in r.text.strip().split('\n'))
        for k, v in rd.items():
            rd[k] = v.strip()

        if rd["Response"] == "Success":
            message_obj.add_state_log(SMSMessageStateLog.State.SUBMITTED_OK)
            span_obj.total_messages_sent += message_obj.pages
            span_obj.total_messages_sent_today += message_obj.pages
            span_obj.total_messages_sent_month += message_obj.pages
            if span_obj.message_failure_count > 0:
                span_obj.message_failure_count = 0
            queued_message.delete()
        elif rd["Response"] == "Failed":
            message_obj.add_state_log(SMSMessageStateLog.State.FAILED, state_reason = f"Failed Response from gateway:  {r.text.strip()}")
            span_obj.message_failure_count += 1
        else:
            message_obj.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Unknown status from gateway: {r.text.strip()}")
            span_obj.message_failure_count += 1
    except ConnectionError as e:
        message_obj.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Connection Error occured {e}")
        span_obj.message_failure_count += 1
    except TimeoutError as e:
        message_obj.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Timeout Error occured {e}")
        span_obj.message_failure_count += 1
    finally:
        span_obj.save()


    
