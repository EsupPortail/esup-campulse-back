"""List of tests done on documents views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.documents.models.document import Document


class DocumentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "commissions_commission.json",
        "documents_document.json",
        "institutions_institution.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

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
