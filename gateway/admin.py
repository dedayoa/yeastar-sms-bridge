from django.contrib import admin
from .models import Device, Span, SendProfile

# Register your models here.
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']

    def get_queryset(self, request):
        qs = super(DeviceAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
class SpanAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel_id', 'SIM_phone_number', 'total_messages_sent', 'total_messages_sent_today', 
    'total_messages_sent_month', 'created', 'message_failure_count', 'sms_sending_disabled']

    readonly_fields = ('total_messages_sent', 'total_messages_sent_today', 'total_messages_sent_month', 'message_failure_count')

    def get_queryset(self, request):
        qs = super(SpanAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)

admin.site.register(Device, DeviceAdmin)
admin.site.register(Span, SpanAdmin)
admin.site.register(SendProfile)