from django.contrib import admin

# Register your models here.
from .models import SMSMessageStateLog, SMSMessage, InvalidSMSMessage, SMSQueue
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse

class SMSMessageResource(resources.ModelResource):
    class Meta:
        model = SMSMessage


def mark_messages_as_new(modeladmin, request, queryset):
    for message in queryset:
        message.status = SMSMessage.Status.NEW
        message.save()

class SMSMessageStateLogAdmin(admin.ModelAdmin):
    list_display = ('sms_id', 'state', 'state_reason', 'timestamp')
    search_fields = ('sms_message_id',)

    def sms_id(self, obj):
        obj_link = reverse("admin:%s_%s_change"%(SMSMessage._meta.app_label, SMSMessage._meta.model_name), args=(obj.sms_message_id,))
        return mark_safe(f'<a href="{obj_link}">{obj.sms_message_id}</a>')
        
class SMSQueueAdmin(admin.ModelAdmin):
    list_display = ['message', 'submit_attempts', 'next_submit_attempt_at', 'created']

class SMSMessageAdmin(ExportActionModelAdmin):
    list_display = ['id', 'bulk_id', 'text', 'recipient', 'pages', 'send_span', 'status', 'created_at']
    search_fields = ('id', 'recipient')
    list_filter = ('status',)
    actions = ExportActionModelAdmin.actions + [mark_messages_as_new]
    resource_class = SMSMessageResource
    
    def get_queryset(self, request):
        qs = super(SMSMessageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
    

admin.site.register(SMSMessageStateLog, SMSMessageStateLogAdmin)
admin.site.register(SMSMessage, SMSMessageAdmin)
admin.site.register(InvalidSMSMessage)
admin.site.register(SMSQueue, SMSQueueAdmin)