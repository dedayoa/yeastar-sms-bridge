from django.apps import AppConfig
from .scheduler import run_schedules


class GatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gateway'

    def ready(self):
        run_schedules()