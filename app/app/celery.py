import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(result_expires=3600,
                enable_utc=False)

app.conf.beat_schedule = {
    "every day": {
        "task": "send_sms_remainder",  # <---- Name of task
        "schedule": crontab(hour=10,
                            minute=00,
                            )
    }
}

app.autodiscover_tasks()
