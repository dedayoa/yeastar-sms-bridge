import django_rq
from datetime import datetime

default_scheduler = django_rq.get_scheduler()

def run_schedules():
    
    default_scheduler.schedule(
        scheduled_time = datetime.utcnow(),
        func = 'gateway.tasks.reset_total_messages_sent_today',
        interval = 5*60,
        repeat = None
        )
