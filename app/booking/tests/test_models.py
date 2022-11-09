from django.test import TestCase
from booking.models import Client


class ModelsTestCase(TestCase):

    def test_phone_number_field(self):
        client_data = {
            "first_name": "Test",
            "second_name": "Name",
            "phone_number": "+48600000000"
        }
        client = Client.objects.create(**client_data)

        for k, v in client_data.items():
            self.assertEqual(getattr(client, k), v)
