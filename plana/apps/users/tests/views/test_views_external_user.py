"""List of tests done with LDAP API endpoint."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class ExternalUserViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/institutions_institution.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    def setUp(self):
        """Initialize default client."""
        self.manager_client = Client()
        self.manager_client.post(
            reverse("rest_login"),
            {
                "username": "gestionnaire-svu@mail.tld",
                "password": "motdepasse",
            },
        )

    @patch('plana.apps.users.views.external.Client')
    def test_external_user_detail_success(self, mock_client):
        """Get an external user."""
        mock_instance = mock_client.return_value
        mock_instance.list_users.return_value = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'mail': 'john.doe@mail.tld',
            }
        ]

        response = self.manager_client.get(reverse('external_user_list'), {'last_name': 'doe'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['mail'], 'john.doe@mail.tld')

    def test_external_user_detail_wrong_permission(self):
        """Don't get an external user if not allowed."""
        student_client = Client()
        student_client.post(
            reverse("rest_login"),
            {
                "username": "president-asso-site@mail.tld",
                "password": "motdepasse",
            },
        )
        response = student_client.get(reverse('external_user_list'), {'last_name': 'jean-doux'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_external_user_detail_missing_last_name(self):
        """Don't get an external user if no last name."""
        response = self.manager_client.get(reverse('external_user_list'), {'wrong': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('plana.apps.users.views.external.Client')
    def test_external_user_detail_empty(self, mock_client):
        """Don't get an external user if nothing is sent."""
        mock_instance = mock_client.return_value
        mock_instance.list_users.return_value = []

        response = self.manager_client.get(reverse('external_user_list'), {'last_name': 'toto'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    @patch('plana.apps.users.views.external.Client', autospec=True)
    def test_external_user_detail_internal_error(self, mock_client):
        """Don't get an external user if exception is thrown."""
        mock_instance = mock_client.return_value
        mock_instance.list_users.side_effect = Exception('error')

        response = self.manager_client.get(reverse('external_user_list'), {'last_name': 'toto'})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
