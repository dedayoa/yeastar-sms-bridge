import django_rq
from datetime import datetime

default_scheduler = django_rq.get_scheduler()

for job in default_scheduler.get_jobs():
    job.delete()

def run_schedules():
    
    default_scheduler.schedule(
        scheduled_time = datetime.utcnow(),
        func = 'sms.tasks.queue_messages',
        interval = 0.25*60,
        repeat = None
        )

    default_scheduler.schedule(
        scheduled_time = datetime.utcnow(),
        func = 'sms.tasks.process_queued_messages',
        interval = 0.1*60,
        repeat = None
        )

    