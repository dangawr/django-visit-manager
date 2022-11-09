import requests
from celery import shared_task, states


@shared_task(name='xxx_execute_xx_task')
def xxx_execute_xx_task():
    # do something
    r = requests.get('https://www.boredapi.com/api/activity')
    return r.status_code
