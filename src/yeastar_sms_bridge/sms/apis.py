import uuid
import phonenumbers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from sms_counter import SMSCounter

from .models import SMSMessage, InvalidSMSMessage, SMSMessageStateLog


class VTigerPluginAPI(APIView):
    """ API to Send SMS """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        data = request.data
        recipients = data.get("to")
        sms_message = data.get("message")
        
        if not recipients or len(recipients) == 0:
            return Response("Recipient(s) missing", status=status.HTTP_400_BAD_REQUEST)
        
        if not sms_message:
            return Response("Message missing", status=status.HTTP_400_BAD_REQUEST)
                                
        result = {
            "messages": [],
            "invalid_numbers": []
            }
        
        # set bulkId
        bulk_id = None
        if len(recipients) > 1:
            bulk_id = data.get("bulkId", uuid.uuid4())
            result["bulkId"] = bulk_id    
        
        counter = SMSCounter.count(data.get("message"))
        
        for recipient in recipients:
            try:
                # this will raise an exception early if number is invalid
                phonenumbers.parse(recipient, None)
                
                m = SMSMessage.objects.create(
                    id = data.get("messageId", uuid.uuid4()),
                    bulk_id = bulk_id,
                    text = data.get("message"),
                    recipient = recipient,
                    user = request.user,
                    pages = counter["messages"]
                    )
                
                result["messages"].append(
                    {
                        "to": str(m.recipient),
                        "submitted": True,
                        "messageId": m.id,
                        "smsCount": m.pages
                        }
                    ) 
            except phonenumbers.phonenumberutil.NumberParseException:
                result["invalid_numbers"].append(recipient)
                raise ValueError(f"Invalid recipient number: {recipient}")
            except ValueError as ve:
                InvalidSMSMessage.objects.create(
                    text = data.get("message"),
                    recipient = recipient,
                    user = request.user,
                    message = m,
                    error_reason = ve
                    )
        return Response(result, status=status.HTTP_201_CREATED)
    
class SMSReport(APIView):
    
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, messageid, format=None):
        m = get_object_or_404(SMSMessage, id=messageid, user=request.user)
        
        result = {}
        #sucessfully sent
        latest_state = m.get_latest_state_log()
        if latest_state == SMSMessageStateLog.State.SUBMITTED_OK:
            result['sent'] = True
            result['to'] = str(m.recipient)
            result['time'] = latest_state.timestamp
        elif latest_state == SMSMessageStateLog.State.ERROR:
            result['error'] = True
            result['errorReason'] = latest_state.state_reason           
        elif latest_state == SMSMessageStateLog.State.FAILED:
            result['failed'] = True
            
        return Response(result)