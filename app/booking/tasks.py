import requests
from celery import shared_task
from booking.models import Visit
import datetime
import os
from django.db.models import F, Count
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
    for user in users:
        visits = Visit.objects.filter(date=tomorrow, client__user=user)
        total_cost = visits.aggregate(total_visits=Count('pk'))['total_visits'] * user.sms_price
        if user.balance >= total_cost:
            token = sms_authenticate_token()
            # Sending sms to clients
            if token:
                for tomorrow_visit in visits:
                    text = f'Hello! \n' \
                           f'We would like to remind you about the visit on {tomorrow_visit.time.strftime("%H:%M")},' \
                           f' {tomorrow.day}.{tomorrow.month} in the {os.environ.get("SMS_API_SENDER")}'
                    sms_send_response = send_sms(client=tomorrow_visit.client, token=token, text=text)
                    if sms_send_response.json()['result'] == 'error':  # If token expired
                        token = sms_authenticate_token()  # Refresh token
                        send_sms(client=tomorrow_visit.client, token=token, text=text)
        user.balance -= total_cost
        user.save(update_fields=['balance'])


    # # App users with clients with visits tomorrow
    # users = Visit.objects.filter(date=tomorrow).values('client')
    # print(users)
    # # App users with clients with visits tomorrow and sms_remainder=True
    # users_with_sms_remainder = users.filter(sms_remainder=True)
    # # App users with clients with visits tomorrow and sms_remainder=True and balance > sms_price * visits_count
    # users_with_correct_balance = users_with_sms_remainder.filter(balance__gte=F('sms_price') * F('visit_count'))
    # # Annotation to app users with count of visits tomorrow
    # users_with_correct_balance.annotate(visit_count=Count('clients__visits').filter(date=tomorrow))

    # for user in users_with_correct_balance:
    #     tomorrow_visits = user.clients.filter(visits__date=tomorrow)
    #
    #     if tomorrow_visits:
    #         sms_message_counter = 0
    #         # Authorization
    #         token = sms_authenticate_token()
    #         # Sending sms to clients
    #         if token:
    #             for tomorrow_visit in tomorrow_visits:
    #                 text = f'Hello! \n' \
    #                        f'We would like to remind you about the visit on {tomorrow_visit.time.strftime("%H:%M")},' \
    #                        f' {tomorrow.day}.{tomorrow.month} in the {os.environ.get("SMS_API_SENDER")}'
    #                 sms_send_response = send_sms(client=tomorrow_visit.client, token=token, text=text)
    #                 if sms_send_response.status_code == 200:
    #                     sms_message_counter += 1
    #                 if sms_send_response.json()['result'] == 'error':  # If token expired
    #                     token = sms_authenticate_token()  # Refresh token
    #                     send_sms(client=tomorrow_visit.client, token=token, text=text)
    #                     sms_message_counter += 1
    #         user.balance -= user.sms_price * sms_message_counter
    #         user.save()  # Update user balance


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
