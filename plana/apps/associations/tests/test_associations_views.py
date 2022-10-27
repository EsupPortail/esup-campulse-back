from django.test import TestCase, Client
from rest_framework import status

class UserTests(TestCase):
    fixtures = ['institutions.json', 'institution_components.json',
                'activity_field.json', 'associations.json']

    def setUp(self):
        self.client = Client()

    def test_get_associations_status_code(self):
        response = self.client.get('/associations/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_associations_by_id_status_code(self):
        response = self.client.get('/associations/1')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

