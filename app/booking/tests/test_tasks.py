# Tests of the tasks module

from unittest.mock import patch
from django.test import TestCase
from booking.tasks import send_sms_remainder, send_sms_visit_cancelled
from booking.models import Visit, Client
import datetime
from django.contrib.auth import get_user_model


@patch('booking.tasks.send_sms')
@patch('booking.tasks.sms_authenticate_token')
class TestTasks(TestCase):

    def setUp(self) -> None:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.user = get_user_model().objects.create_user(username='test', password='test')
        self.client = \
            Client.objects.create(first_name='John', last_name='Doe', phone_number='+48123456789', user=self.user)
        self.visits = \
            [Visit.objects.create(date=tomorrow, time=datetime.time(11, 11), client=self.client) for i in range(3)]

    def test_send_sms_remainder(self, mock_authenticate_token, mock_send_sms):
        mock_authenticate_token.return_value = 'token'
        send_sms_remainder()
        self.assertEqual(mock_send_sms.call_count, 3)

    def test_send_sms_visit_cancelled(self, mock_authenticate_token, mock_send_sms):
        mock_authenticate_token.return_value = 'token'
        send_sms_visit_cancelled(visits_pk=[visit.pk for visit in self.visits], text='test')
        self.assertEqual(mock_send_sms.call_count, 3)
