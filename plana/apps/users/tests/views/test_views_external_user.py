from unittest.mock import patch, Mock

from allauth.account.models import EmailAddress
from rest_framework import status

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class ExternalUserViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            "user",
            email="user@mail.tld",
            password="motdepasse",
        )

        EmailAddress.objects.create(
            user=user,
            email="user@mail.tld",
            verified=True,
            primary=True,
        )

    def setUp(self):
        self.manager_client = Client()
        self.manager_client.post(
            reverse("rest_login"),
            {
                "username": "user",
                "password": "motdepasse",
            },
        )

    @patch('plana.apps.users.views.external.Client')
    def test_external_user_detail_success(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.get_user.return_value = {
            'first_name': 'John',
            'last_name': 'Doe',
            'mail': 'john.doe@mail.tld',
        }

        response = self.manager_client.get(
            reverse('external_user_retrieve'), {'username': 'toto'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mail'], 'john.doe@mail.tld')

    def test_external_user_detail_missing_username(self):
        response = self.manager_client.get(reverse('external_user_retrieve'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('plana.apps.users.views.external.Client')
    def test_external_user_detail_empty(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.get_user.return_value = {}

        response = self.manager_client.get(
            reverse('external_user_retrieve'), {'username': 'toto'}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('plana.apps.users.views.external.Client', autospec=True)
    def test_external_user_detail_internal_error(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.get_user.side_effect = Exception('error')

        response = self.manager_client.get(
            reverse('external_user_retrieve'), {'username': 'toto'}
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
