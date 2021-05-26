from django.apps import AppConfig
from .scheduler import run_schedules


class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sms'
    
    def ready(self):
        run_schedules()
