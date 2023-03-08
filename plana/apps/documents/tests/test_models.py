"""List of tests done on documents models."""
from django.test import Client, TestCase

from plana.apps.documents.models.document import Document


class DocumentsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "documents_document.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_document_model(self):
        """There's at least one document in the database."""
        document = Document.objects.first()
        self.assertEqual(str(document), document.name)
