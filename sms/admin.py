from django.contrib import admin

# Register your models here.
from .models import SMSMessageStateLog, SMSMessage, InvalidSMSMessage, SMSQueue


def mark_messages_as_new(modeladmin, request, queryset):
    for message in queryset:
        message.status = SMSMessage.Status.NEW
        message.save()

class SMSMessageStateLogAdmin(admin.ModelAdmin):
    list_display = ('sms_message_id', 'state', 'state_reason', 'timestamp')
    search_fields = ('sms_message_id',)
class SMSQueueAdmin(admin.ModelAdmin):
    list_display = ['message', 'submit_attempts', 'next_submit_attempt_at', 'created']

class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'bulk_id', 'text', 'recipient', 'pages', 'send_span', 'status', 'created_at']
    search_fields = ('id', 'recipient')
    list_filter = ('status',)
    actions = [mark_messages_as_new]
    
    def get_queryset(self, request):
        qs = super(SMSMessageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
    

admin.site.register(SMSMessageStateLog, SMSMessageStateLogAdmin)
admin.site.register(SMSMessage, SMSMessageAdmin)
admin.site.register(InvalidSMSMessage)
admin.site.register(SMSQueue, SMSQueueAdmin)