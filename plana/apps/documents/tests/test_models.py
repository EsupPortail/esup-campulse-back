"""List of tests done on documents models."""

from django.test import Client, TestCase

from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload


class DocumentsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "commissions_fund.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "users_associationuser.json",
        "users_user.json",
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
