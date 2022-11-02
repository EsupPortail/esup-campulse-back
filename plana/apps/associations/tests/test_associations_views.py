import json

from django.test import TestCase, Client
from rest_framework import status

from ..models import Association

class AssociationsTests(TestCase):
    fixtures = ['institutions.json', 'institution_components.json',
                'activity_fields.json', 'associations.json']

    def setUp(self):
        self.client = Client()

    def test_get_associations_list(self):
        associations_cnt = Association.objects.count()
        self.assertTrue(associations_cnt > 0)

        response = self.client.get('/associations/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), associations_cnt)


    def test_get_association_detail(self):
        association = Association.objects.get(pk=1)

        response = self.client.get('/associations/1')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        association_1 = json.loads(response.content.decode('utf-8'))
        self.assertEqual(association_1["name"], association.name)

