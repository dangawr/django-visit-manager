# Tests of the tasks module

from unittest.mock import patch
from django.test import TestCase
from booking.tasks import send_sms_remainder, send_sms_visit_cancelled
from booking.models import Visit, Client
import datetime
from django.contrib.auth import get_user_model
from decimal import Decimal


@patch('booking.tasks.send_sms')
@patch('booking.tasks.sms_authenticate_token')
class TestTasks(TestCase):

    def setUp(self) -> None:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.user_with_reminder = get_user_model().objects.create_user(
            username='test',
            password='test',
            sms_remainder=True,
            balance=Decimal('10.00'),
        )
        self.user_without_reminder = get_user_model().objects.create_user(
            username='test2',
            password='test2',
            sms_remainder=False,
            balance=Decimal('10.00'),
        )
        self.user_without_balance = get_user_model().objects.create_user(
            username='test3',
            password='test3',
            sms_remainder=True,
            balance=0,
        )
        self.visits_user_with_sms_reminder = \
            [Visit.objects.create(date=tomorrow, time=datetime.time(11, 11), client=Client.objects.create(
                first_name='test1', last_name='Doe', phone_number=f'+4812345578{i}', user=self.user_with_reminder))
             for i in range(3)]
        self.visits_user_without_sms_reminder = \
            [Visit.objects.create(date=tomorrow, time=datetime.time(11, 11), client=Client.objects.create(
                first_name='test2', last_name='Doe', phone_number=f'+4812345678{i}', user=self.user_without_reminder))
             for i in range(3)]
        self.visits_user_without_balance = \
            [Visit.objects.create(date=tomorrow, time=datetime.time(11, 11), client=Client.objects.create(
                first_name='test3', last_name='Doe', phone_number=f'+4812333678{i}', user=self.user_without_balance))
             for i in range(3)]

    def test_send_sms_remainder(self, mock_authenticate_token, mock_send_sms):
        mock_authenticate_token.return_value = 'token'
        balance_with_reminder = \
            self.user_with_reminder.balance - self.user_with_reminder.sms_price * len(self.visits_user_with_sms_reminder)
        send_sms_remainder()
        self.assertEqual(mock_send_sms.call_count, 3)
        self.user_with_reminder.refresh_from_db()
        self.assertEqual(self.user_with_reminder.balance, balance_with_reminder)

    def test_send_sms_visit_cancelled(self, mock_authenticate_token, mock_send_sms):
        mock_authenticate_token.return_value = 'token'
        send_sms_visit_cancelled(
            visits_pk=[visit.pk for visit in self.visits_user_with_sms_reminder],
            text='test',
            user=self.user_with_reminder)
        self.assertEqual(mock_send_sms.call_count, 3)

    def test_send_sms_remainder_no_balance(self, mock_authenticate_token, mock_send_sms):
        mock_authenticate_token.return_value = 'token'
        send_sms_visit_cancelled(
            visits_pk=[visit.pk for visit in self.visits_user_without_balance],
            text='test',
            user=self.user_without_balance)
        self.assertEqual(mock_send_sms.call_count, 0)

    def test_send_sms_remainder_no_sms_reminder(self, mock_authenticate_token, mock_send_sms):
        mock_authenticate_token.return_value = 'token'
        send_sms_visit_cancelled(
            visits_pk=[visit.pk for visit in self.visits_user_without_sms_reminder],
            text='test',
            user=self.user_without_reminder)
        self.assertEqual(mock_send_sms.call_count, 0)
