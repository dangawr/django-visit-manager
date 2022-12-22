from django.test import TestCase
from booking.models import Client
from django.contrib.auth import get_user_model


class ModelsTestCase(TestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123'
        }
        self.user = get_user_model().objects.create_user(**user_details)

    def test_phone_number_field(self):
        client_data = {
            "first_name": "Test",
            "last_name": "Name",
            "phone_number": "+48600000000",
            "user": self.user,
        }
        client = Client.objects.create(**client_data)

        for k, v in client_data.items():
            self.assertEqual(getattr(client, k), v)
