from django.contrib import admin

# Register your models here.
from .models import SMSMessageStateLog, SMSMessage, InvalidSMSMessage, SMSQueue

class SMSQueueAdmin(admin.ModelAdmin):
    list_display = ['message', 'submit_attempts', 'send_span', 'next_submit_attempt_at', 'created']

class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'bulk_id', 'text', 'recipient', 'pages', 'status']
    search_fields = ('id', 'recipient')
    
    def get_queryset(self, request):
        qs = super(SMSMessageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
    

admin.site.register(SMSMessageStateLog)
admin.site.register(SMSMessage, SMSMessageAdmin)
admin.site.register(InvalidSMSMessage)
admin.site.register(SMSQueue, SMSQueueAdmin)