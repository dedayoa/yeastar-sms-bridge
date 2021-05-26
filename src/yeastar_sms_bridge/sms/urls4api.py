from django.urls import path

from .apis import VTigerPluginAPI, SMSReport

urlpatterns = [
    path('text/simple/', VTigerPluginAPI.as_view(), name="vtiger-sms"),
    path('report/<uuid:messageid>/', SMSReport.as_view(), name="sms-status-report")
]