import requests
from celery import shared_task
from booking.models import Visit
import datetime
import os
from django.db.models import Count
from django.contrib.auth import get_user_model


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
    users = get_user_model().objects.filter(sms_remainder=True, balance__gt=0)
    # Check if user has visits tomorrow and if he has enough balance to send sms
    for user in users:
        visits = Visit.objects.filter(date=tomorrow, client__user=user)
        total_cost = visits.aggregate(total_visits=Count('pk'))['total_visits'] * user.sms_price
        if user.balance >= total_cost:
            success_sms_counter = 0
            # Authorization
            token = sms_authenticate_token()
            if token:
                for tomorrow_visit in visits:
                    text = f'Hello! \n' \
                           f'We would like to remind you about the visit on {tomorrow_visit.time.strftime("%H:%M")},' \
                           f' {tomorrow.day}.{tomorrow.month} in the {user.business_name}'
                    while True:
                        # Sending sms to clients
                        sms_send_response = send_sms(client=tomorrow_visit.client, token=token, text=text)
                        # If token expired
                        if sms_send_response.json()['result'] == 'error':
                            # Refresh token
                            token = sms_authenticate_token()
                        if sms_send_response.json()['result'] == 'OK':
                            success_sms_counter += 1
                            break
            user.balance -= success_sms_counter * user.sms_price
            user.save(update_fields=['balance'])


@shared_task
def send_sms_visit_cancelled(visits_pk, text, user):
    if user.sms_remainder and user.balance >= user.sms_price * len(visits_pk):
        visits = Visit.objects.filter(pk__in=visits_pk)
        if visits:
            success_sms_counter = 0
            # Authorization
            token = sms_authenticate_token()
            if token:
                for visit in visits:
                    while True:
                        # Sending sms to clients
                        sms_send_response = send_sms(client=visit.client, token=token, text=text)
                        if sms_send_response.json()['result'] == 'error':
                            token = sms_authenticate_token()
                        if sms_send_response.json()['result'] == 'OK':
                            success_sms_counter += 1
                            break
            user.balance -= success_sms_counter * user.sms_price
            user.save(update_fields=['balance'])

