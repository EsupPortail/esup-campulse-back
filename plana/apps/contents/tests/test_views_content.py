"""List of tests done on contents views."""

import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.contents.models.content import Content


class ContentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "commissions_fund.json",
        "contents_content.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "institutions_institution.json",
        "users_user.json",
        "users_groupinstitutionfunduser.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on most tests."""
        cls.client = Client()
        url_login = reverse("rest_login")

        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.general_client = Client()
        data_general = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.general_client.post(url_login, data_general)

        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

    def test_get_contents_list(self):
        """
        GET /contents/ .

        - There's at least one content in the contents list.
        - The route can be accessed by anyone.
        - We get the same amount of contents through the model and through the view.
        - Contents details are returned (test the "code" attribute).
        - Filter by code is available.
        - Filter by is_editable is available.
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
        self.assertEqual(response.data[0]["is_editable"], True)

        response = self.client.get("/contents/?is_editable=false")
        self.assertEqual(response.data[0]["is_editable"], False)
        self.assertNotEqual(response.data[0]["code"], code)

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

    def test_put_content(self):
        """
        PUT /contents/{id} .

        - Always returns a 405 no matter which user tries to access it.
        """
        response = self.client.put(
            "/contents/1", {"body": "Bienvenue sur Campulse, le site de la vie associative étudiante de l'UNISTRA"}
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_content_anonymous(self):
        """
        PATCH /contents/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.patch(
            "/contents/1",
            {"body": "L'application Campulse a vu le jour en Septembre 2023."},
            content_type="application/json",
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_contents_serializer_error(self):
        """
        PATCH /contents/{id} .

        - A user with proper permissions can execute this request.
        - Serializers fields must be valid.
        """
        patch_data = {"body": False}
        response = self.general_client.patch("/contents/1", data=patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_contents_forbidden_fund(self):
        """
        PATCH /contents/{id} .

        - A user without permission can't execute this request.
        """
        patch_data = {"body": "Déposez vos chartes Site Alsace, FSDIE, IdEx et Culture-ActionS sur Campulse."}
        response = self.institution_client.patch("/contents/1", data=patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_uneditable_content(self):
        """
        PATCH /contents/{id} .

        - A user with proper permissions can execute this request.
        - Content must be editable.
        """
        patch_data = {"body": "Veuillez confirmer la création de votre compte avant de le faire valider ou rejeter."}
        response = self.general_client.patch("/contents/29", data=patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_contents_success(self):
        """
        PATCH /contents/{id} .

        - A general manager can edit contents.
        """
        content_id = 1
        patch_data = {"body": "Campulse"}
        response = self.general_client.patch(
            f"/contents/{content_id}", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = Content.objects.get(id=content_id)
        self.assertEqual(content.body, "Campulse")
