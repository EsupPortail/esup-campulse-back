from django.test import TestCase, Client

class UserTests(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.client = Client()

    def test_get_users_status_code(self):
        response = self.client.get('/users/')
        self.assertEquals(response.status_code, 200)

    def test_get_users_by_id_status_code(self):
        response = self.client.get('/users/1')
        self.assertEquals(response.status_code, 200)

