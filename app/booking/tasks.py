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


def send_sms(client, token, text):
    headers = {'Authorization': f'Bearer {token}'}
    sms_data = {
        'from': os.environ.get('SMS_API_SENDER'),
        'to': client.phone_number.as_e164.strip('+'),
        'text': text
    }
    return requests.post(url='https://api.vpbx.pl/api/v1/sms', json=sms_data, headers=headers)


@shared_task(name='send_sms_remainder')
def send_sms_remainder():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_visits = Visit.objects.filter(date=tomorrow)

    if tomorrow_visits:
        # Authorization
        token = sms_authenticate_token()
        # Sending sms to clients
        if token:
            for tomorrow_visit in tomorrow_visits:
                text = f'Hello! \n' \
                       f'We would like to remind you about the visit on {tomorrow_visit.time.strftime("%H:%M")},' \
                       f' {tomorrow.day}.{tomorrow.month} in the {os.environ.get("SMS_API_SENDER")}'
                sms_send_response = send_sms(client=tomorrow_visit.client, token=token, text=text)
                if sms_send_response.json()['result'] == 'error':  # If token expired
                    token = sms_authenticate_token()  # Refresh token
                    send_sms(client=tomorrow_visit.client, token=token, text=text)


@shared_task
def send_sms_visit_cancelled(visits_pk, text):
    visits = Visit.objects.filter(pk__in=visits_pk)
    if visits:
        # Authorization
        token = sms_authenticate_token()
        # Sending sms to clients
        if token:
            for visit in visits:
                sms_send_response = send_sms(client=visit.client, token=token, text=text)
                if sms_send_response.json()['result'] == 'error':
                    token = sms_authenticate_token()
                    send_sms(client=visit.client, token=token, text=text)
