import django_rq
from datetime import datetime

default_scheduler = django_rq.get_scheduler()


def run_schedules():
    
    default_scheduler.schedule(
        scheduled_time = datetime.utcnow(),
        func = 'sms.tasks.queue_messages',
        interval = 1*60,
        repeat = None
        )