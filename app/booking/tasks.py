import requests
from celery import shared_task
from booking.models import Visit
import datetime
import os


def sms_authenticate_token():
    auth_response = requests.post(
        url='https://api.vpbx.pl/api/v1/login',
        json={"username": os.environ.get('SMS_API_USER'), "password": os.environ.get('SMS_API_PASSWORD')}
    )
    return auth_response.json()['token']


def send_sms(client, date, token, visit):
    headers = {'Authorization': f'Bearer {token}'}
    sms_data = {
        'from': os.environ.get('SMS_API_SENDER'),
        'to': client.phone_number.as_e164.strip('+'),
        'text':
            f'Hello! \n'
            f'We would like to remind you about the visit on {visit.time.strftime("%H:%M")},'
            f' {date.day}.{date.month} in the {os.environ.get("SMS_API_SENDER")}'
    }
    return requests.post(url='https://api.vpbx.pl/api/v1/sms', json=sms_data, headers=headers)


@shared_task(name='send_sms_remainder')
def send_sms_remainder():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    today_visits = Visit.objects.filter(date=tomorrow)

    if today_visits:
        # Authorization
        token = sms_authenticate_token()

        # Sending sms to clients
        if token:
            for today_visit in today_visits:
                sms_send_response = send_sms(client=today_visit.client, date=tomorrow, token=token, visit=today_visit)
                if sms_send_response.json()['result'] == 'error':   # If token expired
                    token = sms_authenticate_token()                # Refresh token
                    send_sms(client=today_visit.client, date=tomorrow, token=token, visit=today_visit)
