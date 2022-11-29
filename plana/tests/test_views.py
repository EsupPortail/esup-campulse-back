from rest_framework import status
from django.test import TestCase, Client


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_plana_views(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode("utf-8")

        # self.assertIn("", content) #FIXME wait for content to be tested
