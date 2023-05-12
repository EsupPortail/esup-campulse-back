"""List of tests done on associations views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.contents.models.content import Content


class ContentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_commission.json",
        "contents_content.json",
        "institutions_institution.json",
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # Start a default client used on most tests.
        cls.client = Client()
        url_login = reverse("rest_login")

        # Start a default client used on access tests.
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.student_client = Client()
        data_student = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_client.post(url_login, data_student)

        # Start a manager client used in some tests
        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.manager_client = Client()
        data_manager = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response_manager = cls.manager_client.post(url_login, data_manager)

    def test_get_contents_list(self):
        """
        GET /contents/ .

        - There's at least one content in the contents list.
        - The route can be accessed by anyone.
        - We get the same amount of contents through the model and through the view.
        - Contents details are returned (test the "code" attribute).
        - Filter by code is available.
        """
        contents_cnt = Content.objects.count()
        self.assertTrue(contents_cnt > 0)

        response = self.client.get("/contents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), contents_cnt)

        content_1 = content[0]
        self.assertTrue(content_1.get("code"))

        code = "HOME_INFO"
        response = self.client.get(f"/contents/?code={code}")
        self.assertEqual(response.data[0]["code"], code)

    def test_get_unexisting_content(self):
        """
        GET /contents/{id} .

        - 404 error if content not found.
        """
        cid = 999
        response = self.client.get(f"/contents/{cid}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_content_details(self):
        """
        GET /contents/{id} .

        - The route can be accessed by anyone.
        - All content details are returned.
        - Correct content details are returned.
        """
        cid = 1
        response = self.client.get(f"/contents/{cid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data.get("code"))
        self.assertTrue(response.data.get("label"))
        self.assertTrue(response.data.get("body"))

        content = Content.objects.get(id=cid)
        self.assertEqual(content.code, response.data["code"])
