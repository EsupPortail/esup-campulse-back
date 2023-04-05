"""List of tests done on documents views."""
from unittest.mock import Mock

from django.core.files.storage import default_storage
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.documents.models.document_upload import DocumentUpload
from plana.storages import DynamicStorageFieldFile


class DocumentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_commission.json",
        "documents_document.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default anonymous client."""
        cls.client = Client()
        url_login = reverse("rest_login")

        """ Start a manager general client used on a majority of tests. """
        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.general_client = Client()
        data_general = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.general_client.post(url_login, data_general)

        """ Start a user misc that can update documents for projects. """
        cls.student_misc_user_id = 9
        cls.student_misc_user_name = "etudiant-porteur@mail.tld"
        cls.student_misc_client = Client()
        data_student_misc = {
            "username": cls.student_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_misc_client.post(url_login, data_student_misc)

    def test_get_document_upload_list_anonymous(self):
        """
        GET /documents/uploads .
        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/documents/uploads")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_document_upload_project_anonymous(self):
        """
        POST /documents/uploads .
        - An anonymous user cannot execute this request.
        """
        post_data = {
            "path_file": "",
            "project": 9999,
            "document": 14,
        }
        response = self.client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_document_upload_project_not_found(self):
        """
        POST /documents/uploads .
        - The route can be accessed by any authenticated user.
        - The project edited must be existing.
        """
        post_data = {
            "path_file": "",
            "project": 9999,
            "document": 14,
        }
        response = self.general_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_document_upload_forbidden_project(self):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        """
        post_data = {
            "path_file": "",
            "project": 1,
            "document": 14,
        }
        response = self.general_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_document_upload_project_success(self):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        - Object is correctly created in db.
        """
        """
        project_id = 1
        document_id = 14
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()
        post_data = {
            "path_file": file,
            "project": project_id,
            "document": document_id,
        }
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        du_cnt = len(
            DocumentUpload.objects.filter(
                project_id=project_id, document_id=document_id
            )
        )
        self.assertEqual(du_cnt, 1)
        """
