from django.test import TestCase
from django.urls import reverse
from booking.models import Visit, Client
from django.contrib.auth import get_user_model
import datetime
from unittest.mock import patch


def create_visit(client, date, time, notes):
    """
    Create a visit with the given `client`, `date`, `time` and `notes`.
    """
    return Visit.objects.create(client=client, date=date, time=time, notes=notes)


def create_client(user, first_name, last_name, phone_number,):
    """
    Create a client with the given `user`, `first_name`, `last_name`, `phone` and `email`.
    """
    return Client.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number
    )


class VisitCrudTestCase(TestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123'
        }
        self.user = get_user_model().objects.create_user(**user_details)
        self.client.force_login(user=self.user)
        self.other_user_visit = create_visit(
                client=create_client(
                    user=get_user_model().objects.create_user(username='other_user', password='test-user-password123'),
                    first_name='Other',
                    last_name='User',
                    phone_number='+48123457666',
                ),
                date=datetime.date.today(),
                time=datetime.time(10, 0),
                notes='Test notes')

    def test_list_view_with_no_visits(self):
        """
        If no visits exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('booking:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [])

    def test_list_view_with_visits(self):
        """
        If visits exist, they should be displayed.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )
        visit = create_visit(
            client=client,
            date=datetime.date.today(),
            time=datetime.time(10, 0),
            notes='Test notes'
        )

        response = self.client.get(reverse('booking:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [visit])

    def test_list_view_with_future_visits(self):
        """
        If future visits exist, they should be displayed.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )
        visit = create_visit(
            client=client,
            date=datetime.date.today() + datetime.timedelta(days=1),
            time=datetime.time(10, 0),
            notes='Test notes'
        )

        response = self.client.get(reverse('booking:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [])

        response = self.client.get(reverse('booking:index') + '?date=' + str(visit.date))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [visit])

    def test_update_visit_view(self):
        """
        If a visit exists, it should be updated.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )
        visit = create_visit(
            client=client,
            date=datetime.date.today(),
            time=datetime.time(10, 0),
            notes='Test notes'
        )

        response = self.client.get(reverse('booking:visit-edit', args=[visit.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:visit-edit', args=[visit.id]), {
            'date': datetime.date.today(),
            'time': datetime.time(11, 0),
            'client': client.id,
            'notes': 'Updated notes'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.get(id=visit.id).notes, 'Updated notes')

    def test_update_other_user_visit_view(self):
        """
        If a visit exists, it should not be updated.
        """
        response = self.client.get(reverse('booking:visit-edit', args=[self.other_user_visit.id]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('booking:visit-edit', args=[self.other_user_visit.id]), {
            'date': datetime.date.today(),
            'time': datetime.time(11, 0),
            'client': self.other_user_visit.client.id,
            'notes': 'Updated notes'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Visit.objects.get(id=self.other_user_visit.id).notes, 'Test notes')

    def test_create_visit_view(self):
        """
        If a visit does not exist, it should be created.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )

        response = self.client.get(reverse('booking:visit-create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:visit-create'), {
            'date': datetime.date.today(),
            'time': datetime.time(11, 0),
            'client': client.id,
            'notes': 'Updated notes'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.filter(client__user=self.user).count(), 1)

    def test_delete_visit_view(self):
        """
        If a visit exists, it should be deleted.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )
        visit = create_visit(
            client=client,
            date=datetime.date.today(),
            time=datetime.time(10, 0),
            notes='Test notes'
        )

        response = self.client.get(reverse('booking:visit-delete', args=[visit.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:visit-delete', args=[visit.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.filter(client__user=self.user).count(), 0)

    def test_delete_other_user_visit_view(self):
        """
        If a visit exists, it should not be deleted.
        """
        response = self.client.get(reverse('booking:visit-delete', args=[self.other_user_visit.id]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('booking:visit-delete', args=[self.other_user_visit.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Visit.objects.filter(client__user=self.other_user_visit.client.user).count(), 1)


class ClientCrudTestCase(TestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123'
        }
        self.user = get_user_model().objects.create_user(**user_details)
        self.client.force_login(user=self.user)
        self.other_user_client = create_client(
            first_name='Other',
            last_name='Client',
            phone_number='+48123444789',
            user=get_user_model().objects.create_user(
                username='Other User',
                password='other-user-password123'
            )
        )

    def test_list_view_with_no_clients(self):
        """
        If no clients exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('booking:clients'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [])

    def test_list_view_with_clients(self):
        """
        If clients exist, they should be displayed.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )

        response = self.client.get(reverse('booking:clients'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [client])

    def test_create_client_view(self):
        """
        If a client does not exist, it should be created.
        """
        response = self.client.get(reverse('booking:client-create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:client-create'), {
            'first_name': 'Updated first name',
            'last_name': 'Updated last name',
            'phone_number': '+48123456789'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.filter(user=self.user).count(), 1)

    def test_update_client_view(self):
        """
        If a client exists, it should be updated.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )

        response = self.client.get(reverse('booking:client-edit', args=[client.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:client-edit', args=[client.id]), {
            'first_name': 'Updated first name',
            'last_name': 'Updated last name',
            'phone_number': '+48123456789'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.get(id=client.id).first_name, 'Updated first name')

    def test_update_other_user_client_view(self):
        """
        If a client exists, it should not be updated.
        """
        response = self.client.get(reverse('booking:client-edit', args=[self.other_user_client.id]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('booking:client-edit', args=[self.other_user_client.id]), {
            'first_name': 'Updated first name',
            'last_name': 'Updated last name',
            'phone_number': '+48123456789'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Client.objects.get(id=self.other_user_client.id).first_name, 'Other')

    def test_delete_client_view(self):
        """
        If a client exists, it should be deleted.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )

        response = self.client.get(reverse('booking:client-delete', args=[client.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:client-delete', args=[client.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.filter(user=self.user).count(), 0)

    def test_delete_other_user_client_view(self):
        """
        If a client exists, it should not be deleted.
        """
        response = self.client.get(reverse('booking:client-delete', args=[self.other_user_client.id]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('booking:client-delete', args=[self.other_user_client.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Client.objects.filter(user=self.other_user_client.user).count(), 1)

    def test_clients_filter(self):
        """
        If clients exist, they should be filtered.
        """
        client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )
        second_client = create_client(
            user=self.user,
            first_name='Second',
            last_name='Person',
            phone_number='+48123456788'
        )

        # Filter by first name
        response = self.client.get(reverse('booking:clients'), {'search': client.first_name})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [client])
        self.assertNotIn(response.context['object_list'], [second_client])

        # Filter by last name
        response = self.client.get(reverse('booking:clients'), {'search': client.last_name})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [client])
        self.assertNotIn(response.context['object_list'], [second_client])

        # Filter by phone number
        response = self.client.get(reverse('booking:clients'), {'search': str(client.phone_number)})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [client])
        self.assertNotIn(response.context['object_list'], [second_client])

        # Filter by first and last name
        response = self.client.get(reverse('booking:clients'), {'search': f'{client.first_name} {client.last_name}'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [client])
        self.assertNotIn(response.context['object_list'], [second_client])

        # Filter by last and first name
        response = self.client.get(reverse('booking:clients'), {'search': f'{client.last_name} {client.first_name}'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [client])
        self.assertNotIn(response.context['object_list'], [second_client])


class SignInViewTest(TestCase):

    def test_sign_in_view(self):
        """
        If a user does not exist, it should be created.
        """
        response = self.client.get(reverse('booking:signin'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:signin'), {
            'username': 'Test',
            'password1': 'Testowy!2345',
            'password2': 'Testowy!2345'

        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.count(), 1)


class LoginViewTestCase(TestCase):

    def setUp(self):
        self.user_details = {
            'username': 'testname',
            'password': 'qwe123'
        }
        self.user = get_user_model().objects.create_user(**self.user_details)

    def test_login_view(self):
        """
        If a user exists, it should be logged in.
        """
        response = self.client.get(reverse('booking:login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:login'), {
            'username': self.user_details['username'],
            'password': self.user_details['password']
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))


class LogoutViewTestCase(TestCase):

    def setUp(self):
        self.user_details = {
            'username': 'testname',
            'password': 'qwe123'
        }
        self.user = get_user_model().objects.create_user(**self.user_details)
        self.client.force_login(self.user)

    def test_logout_view(self):
        """
        If a user is logged in, it should be logged out.
        """
        response = self.client.get(reverse('booking:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


@patch('booking.views.send_sms_visit_cancelled.delay')
class CancelVisitsViewTestCase(TestCase):

    def setUp(self):
        self.user_details = {
            'username': 'testname',
            'password': 'qwe123'
        }
        self.user = get_user_model().objects.create_user(**self.user_details)
        self.client.force_login(self.user)
        self.visit_client = create_client(
            user=self.user,
            first_name='Test',
            last_name='Client',
            phone_number='+48123456789'
        )
        today = datetime.date.today()
        self.visits = \
            [create_visit(date=today, time=datetime.time(11, 11), client=self.visit_client, notes='') for i in range(3)]

    def test_cancel_visits_view_with_send_sms_with_text(self, mock_send_sms_visit_cancelled):
        """
        If visits exist, they should be cancelled.
        """
        response = self.client.get(reverse('booking:cancel-visits'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:cancel-visits'), {
            'from_date': datetime.date.today(),
            'to_date': datetime.date.today(),
            'send_sms': True,
            'text_message': 'Test message'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.count(), 0)
        self.assertEqual(mock_send_sms_visit_cancelled.call_count, 1)

    def test_cancel_visits_view_with_send_sms_without_text(self, mock_send_sms_visit_cancelled):
        """
        If visits exist, they should be cancelled.
        """
        response = self.client.get(reverse('booking:cancel-visits'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:cancel-visits'), {
            'from_date': datetime.date.today(),
            'to_date': datetime.date.today(),
            'send_sms': True,
            'text_message': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required', response.context['form'].errors['text_message'])
        self.assertEqual(Visit.objects.count(), 3)
        self.assertEqual(mock_send_sms_visit_cancelled.call_count, 0)

    def test_cancel_visits_view_without_send_sms(self, mock_send_sms_visit_cancelled):
        """
        If visits exist, they should be cancelled.
        """
        response = self.client.get(reverse('booking:cancel-visits'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:cancel-visits'), {
            'from_date': datetime.date.today(),
            'to_date': datetime.date.today(),
            'send_sms': False,
            'text_message': 'Test message'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.count(), 0)
        self.assertEqual(mock_send_sms_visit_cancelled.call_count, 0)

    def test_cancel_visits_view_with_wrong_dates(self, mock_send_sms_visit_cancelled):
        """
        If visits exist, they should be cancelled.
        """
        response = self.client.get(reverse('booking:cancel-visits'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('booking:cancel-visits'), {
            'from_date': datetime.date.today() + datetime.timedelta(days=1),
            'to_date': datetime.date.today() + datetime.timedelta(days=2),
            'send_sms': False,
            'text_message': 'Test message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('No visits found for this period', response.context['form'].errors['__all__'])
        self.assertEqual(Visit.objects.count(), 3)
        self.assertEqual(mock_send_sms_visit_cancelled.call_count, 0)

