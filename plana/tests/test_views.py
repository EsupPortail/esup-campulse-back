from django.test import Client, TestCase
from rest_framework import status


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_plana_views(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode("utf-8")

        # self.assertIn("", content) # wait for content to be tested
