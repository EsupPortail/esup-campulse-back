"""List of tests done on documents views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.documents.models.document import Document


class DocumentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_commission.json",
        "documents_document.json",
        "institutions_institution.json",
        "users_groupinstitutioncommissionusers.json",
        "users_user.json",
    ]

    def setUp(self):
        """Start a default anonymous client."""
        self.client = Client()
        url_login = reverse("rest_login")

        """ Start a manager general client used on a majority of tests. """
        self.manager_general_user_id = 3
        self.manager_general_user_name = "gestionnaire-svu@mail.tld"
        self.general_client = Client()
        data_general = {
            "username": self.manager_general_user_name,
            "password": "motdepasse",
        }
        self.response = self.general_client.post(url_login, data_general)

        """ Start a manager institution client used on some permissions tests. """
        self.manager_institution_user_id = 3
        self.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        self.institution_client = Client()
        data_institution = {
            "username": self.manager_institution_user_name,
            "password": "motdepasse",
        }
        self.response = self.institution_client.post(url_login, data_institution)

    def test_get_documents_list(self):
        """
        GET /documents/ .

        - There's at least one document in the documents list.
        - The route can be accessed by anyone.
        - We get the same amount of documents through the model and through the view.
        - Documents details are returned (test the "name" attribute).
        """
        documents_cnt = Document.objects.count()
        self.assertTrue(documents_cnt > 0)

        response = self.client.get("/documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

        document_1 = content[0]
        self.assertTrue(document_1.get("name"))

    def test_get_document_by_id_anonymous(self):
        """
        GET /documents/{id} .

        - An anonymous user can execute this request.
        """
        response = self.client.get("/documents/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_document_by_id(self):
        """
        GET /documents/{id} .

        - The route can be accessed by any authenticated user.
        - Correct documents details are returned (test the "name" attribute).
        """
        document_id = 1
        doc_test = Document.objects.get(id=document_id)
        response = self.general_client.get(f"/documents/{document_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        document = content
        self.assertEqual(document["name"], doc_test.name)

    def test_get_document_by_id_404(self):
        """
        GET /documents/{id} .

        - The route returns a 404 if a wrong document id is given.
        """
        response = self.general_client.get("/documents/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_document_by_id_anonymous(self):
        """
        DELETE /documents/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/documents/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_document_by_id(self):
        """
        DELETE /documents/{id} .

        - The route can be accessed by an authenticated user with correct permissions.
        - The document is correctly deleted.
        """
        document_id = 1
        response = self.general_client.delete(f"/documents/{document_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        doc_deleted = Document.objects.filter(id=document_id)
        self.assertEqual(len(doc_deleted), 0)

    def test_delete_document_by_id_forbidden_institution(self):
        """
        DELETE /documents/{id} .

        - A document linked to an institution cannot be deleted by a user who's not linked to the same institution.
        """
        document_id = 1
        response = self.institution_client.delete(f"/documents/{document_id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_document_by_id_404(self):
        """
        DELETE /documents/{id} .

        - The route returns a 404 if a wrong document id is given.
        """
        response = self.general_client.delete("/documents/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
