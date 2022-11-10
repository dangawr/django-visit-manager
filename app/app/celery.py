import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.beat_schedule = {
#     "every day between 6 AM & 18 PM": {
#         "task": "xxx_execute_xx_task",  # <---- Name of task
#         "schedule": crontab(hour=15,
#                             minute=47,
#                             )
#     }
# }

app.autodiscover_tasks()
