import requests
from django.conf import settings
from gateway.models import SendProfile, Span

from sms.models import SMSMessage, SMSMessageStateLog, SMSQueue
from requests.exceptions import ConnectionError


def parse_response_from_gateway(response):
    try:
        lines = response.strip().split('\n')
        result = (lines[0].split(":")[1]).strip().lower()
        if result not in ["failed", "success", "error"]:
            return None
        return result
    except IndexError:
        return None
    

def yeastar_sms_send(queued_message):
    
    message = queued_message.message
    span = message.send_span

    url = span.device.api_url
    
    payload = {
        'account': span.device.api_username,
        'password': span.device.api_password,
        'port': span.port_id(),
        'destination': str(message.recipient),
        'content': str(message.text)
    }
    rf_gw = None
    try:
        r = requests.get(url, params=payload, timeout = settings.MAX_GATEWAY_HTTP_TIMEOUT)
        if r.status_code == 200:
            rf_gw = parse_response_from_gateway(r.text)
            if rf_gw == "success":
                message.add_state_log(SMSMessageStateLog.State.SUBMITTED_OK)
                span.total_messages_sent += message.pages
                span.total_messages_sent_today += message.pages
                span.total_messages_sent_month += message.pages
                if span.message_failure_count > 0:
                    span.message_failure_count = 0
                queued_message.delete()
            elif rf_gw == "failed":
                message.add_state_log(SMSMessageStateLog.State.FAILED, state_reason = f"Failed Response from gateway:  {r.text.strip()}")
                span.message_failure_count += 1
            elif rf_gw == "error":
                message.add_state_log(SMSMessageStateLog.State.FAILED, state_reason = f"Error Response from gateway:  {r.text.strip()}")
                span.message_failure_count += 1
            else:
                message.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Unknown status from gateway: {r.text.strip()}")
                span.message_failure_count += 1
        else:
            message.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Gateway returned {r.status_code} http code")
            span.message_failure_count += 1
    except ConnectionError as e:
        message.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Connection Error occured {e}")
        span.message_failure_count += 1
    except TimeoutError as e:
        message.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Timeout Error occured {e}")
        span.message_failure_count += 1
    except Exception as e:
        message.add_state_log(SMSMessageStateLog.State.ERROR, state_reason = f"Some Error occured {e}")
        span.message_failure_count += 1
    finally:
        span.save()

#TODO: user has multiple gateway devices
def get_span_by_profile(user_id):
    default_profile = SendProfile.objects.get(user = user_id, is_default = True)
    if default_profile.strategy == SendProfile.SendStrategy.SINGLE:
        return default_profile.spans.all()[0]
    #TODO: complete implmentation for random and distribute
    return default_profile.spans.all()[0]

