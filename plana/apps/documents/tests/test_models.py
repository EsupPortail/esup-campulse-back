"""List of tests done on documents models."""

from django.test import Client, TestCase

from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload


class DocumentsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "associations_activityfield.json",
        "tests/associations_association.json",
        "tests/commissions_fund.json",
        "tests/documents_document.json",
        "tests/documents_documentupload.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "tests/projects_project.json",
        "tests/users_associationuser.json",
        "tests/users_user.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_document_model(self):
        """There's at least one document in the database."""
        document = Document.objects.first()
        self.assertEqual(str(document), document.acronym)

    def test_document_upload_model(self):
        """There's at least one document upload in the database."""
        document_upload = DocumentUpload.objects.first()
        self.assertEqual(str(document_upload), document_upload.name)
