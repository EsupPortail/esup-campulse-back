"""List of tests done on documents views."""
import json
from unittest.mock import Mock, patch

from django.core.files.storage import default_storage
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.users.models.user import AssociationUser
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
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start clients used on tests."""
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

        cls.student_misc_user_id = 9
        cls.student_misc_user_name = "etudiant-porteur@mail.tld"
        cls.student_misc_client = Client()
        data_student_misc = {
            "username": cls.student_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_misc_client.post(url_login, data_student_misc)

        cls.student_site_user_id = 11
        cls.student_site_user_name = "etudiant-asso-site@mail.tld"
        cls.student_site_client = Client()
        data_student_site = {
            "username": cls.student_site_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_site_client.post(url_login, data_student_site)

        cls.student_president_user_id = 13
        cls.student_president_user_name = "president-asso-site@mail.tld"
        cls.student_president_client = Client()
        data_student_president = {
            "username": cls.student_president_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_president_client.post(
            url_login, data_student_president
        )

    def test_get_document_upload_list_anonymous(self):
        """
        GET /documents/uploads .
        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/documents/uploads")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_document_upload_list_student(self):
        """
        GET /documents/uploads .

        - A student user gets documents where rights are OK.
        """
        response = self.student_misc_client.get("/documents/uploads")
        user_associations_ids = AssociationUser.objects.filter(
            user_id=self.student_misc_user_id
        ).values_list("association_id")
        user_documents_cnt = DocumentUpload.objects.filter(
            models.Q(user_id=self.student_misc_user_id)
            | models.Q(association_id__in=user_associations_ids)
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), user_documents_cnt)

    def test_get_project_manager(self):
        """
        GET /documents/uploads .

        - A general manager user gets all documents uploads.
        - user, association and project filters work.
        """
        response = self.general_client.get("/documents/uploads")
        documents_cnt = DocumentUpload.objects.all().count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), documents_cnt)

        response = self.general_client.get(
            f"/documents/uploads?user_id={self.student_misc_user_id}"
        )
        documents_cnt = DocumentUpload.objects.filter(
            user_id=self.student_misc_user_id
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

        association_id = 2
        response = self.general_client.get(
            f"/documents/uploads?association_id={association_id}"
        )
        documents_cnt = DocumentUpload.objects.filter(
            association_id=association_id
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

        project_id = 1
        response = self.general_client.get(
            f"/documents/uploads?project_id={project_id}"
        )
        documents_cnt = DocumentUpload.objects.filter(project_id=project_id).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

    def test_post_document_upload_project_anonymous(self):
        """
        POST /documents/uploads .
        - An anonymous user cannot execute this request.
        """
        post_data = {
            "path_file": "",
            "project": 9999,
            "document": 16,
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
            "document": 16,
        }
        response = self.general_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_document_upload_document_not_found(self):
        """
        POST /documents/uploads .
        - The route can be accessed by any authenticated user.
        - The document linked must be existing.
        """
        post_data = {
            "path_file": "",
            "document": 9999,
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
            "document": 16,
        }
        response = self.general_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_document_upload_bad_request(self):
        """
        POST /documents/uploads .

        - The route can be accessed by a student user.
        - Document must have at least one affectation (user or association).
        - If linked to an association, the association must already exist.
        - Document cannot have multiple affectations.
        """
        document_data = {
            "path_file": "",
            "document": 16,
        }
        response = self.student_site_client.post("/documents/uploads", document_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        document_data["association"] = 9999
        response = self.student_site_client.post("/documents/uploads", document_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        document_data["association"] = 2
        document_data["user"] = self.student_president_user_id
        response = self.student_president_client.post(
            "/documents/uploads", document_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_document_upload_forbidden_user(self):
        """
        POST /documents/uploads .

        - The route can be accessed by a student user.
        - User in the request must be the authenticated user.
        """
        document_data = {"path_file": "", "document": 16, "user": 2}
        response = self.student_site_client.post("/documents/uploads", document_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_document_upload_forbidden_association_role(self):
        """
        POST /documents/uploads .

        - The route can be accessed by a student user.
        - The authenticated user must be a member of the association to post documents related to it.
        - User must be president or delegated president of its association to post documents.
        """
        document_data = {"path_file": "", "document": 16, "association": 2}
        response = self.student_site_client.post("/documents/uploads", document_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_document_upload_no_document(self):
        """
        POST /documents/uploads .

        - The route can be accessed by a student user.
        - Document must be set.
        """
        document_data = {"path_file": "", "user": self.student_misc_user_id}
        response = self.student_site_client.post("/documents/uploads", document_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_document_upload_multiple(self):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        - Object is correctly created in db.
        """
        project_id = 1
        document_id = 16
        post_data = {
            "path_file": "",
            "project": project_id,
            "document": document_id,
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('plana.storages.UpdateACLStorage.update_acl')
    def test_post_document_upload_project_success(self, update_acl):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        - Object is correctly created in db.
        """
        project_id = 1
        document_id = 20
        update_acl.return_value = Mock()
        document = Document.objects.get(id=document_id)
        document.mime_types = ["application/vnd.novadigm.ext"]
        document.save()
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()
        post_data = {
            "path_file": file,
            "project": project_id,
            "document": document_id,
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        du_cnt = len(
            DocumentUpload.objects.filter(
                project_id=project_id, document_id=document_id
            )
        )
        self.assertEqual(du_cnt, 2)

    def test_get_document_upload_by_id_anonymous(self):
        """
        GET /documents/uploads/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/documents/uploads/2")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_document_upload_by_id_forbidden_student(self):
        """
        GET /documents/uploads/{id} .

        - An student user not owning the document cannot execute this request.
        """
        response = self.student_misc_client.get("/documents/uploads/6")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_document_upload_by_id(self):
        """
        GET /documents/uploads/{id} .

        - The route can be accessed by a manager user.
        - Correct documents details are returned (test the "document" attribute).
        """
        # TODO Find how to fixture document.
        """
        document_upload_id = 1
        document_upload = DocumentUpload.objects.get(id=document_upload_id)
        response = self.general_client.get(f"/documents/uploads/{document_upload_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["document"], document_upload.document_id)
        """

    def test_get_document_upload_by_id_404(self):
        """
        GET /documents/uploads/{id} .

        - The route returns a 404 if a wrong document upload id is given.
        """
        response = self.general_client.get("/documents/uploads/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_document_upload_anonymous(self):
        """
        DELETE /documents/uploads/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/documents/uploads/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_document_upload_not_found(self):
        """
        DELETE /documents/uploads/{id} .

        - The route can be accessed by a student user.
        - The document upload must be existing.
        """
        response = self.student_misc_client.delete("/documents/uploads/999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_document_upload_forbidden_user(self):
        """
        DELETE /documents/uploads/{id} .

        - The route can be accessed by a student user.
        - The owner of the project must be the authenticated user.
        """
        document_upload_id = 6
        response = self.student_misc_client.delete(
            f"/documents/uploads/{document_upload_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_document_upload_association_success(self):
        """
        DELETE /documents/uploads/{id} .

        - The route can be accessed by a student user.
        - The authenticated user must be the president of the association owning the document.
        - The DocumentUpload is deleted from db.
        - If the same DocumentUpload is attempted to be deleted, returns a HTTP 404.
        """
        document_upload_id = 6
        response = self.student_president_client.delete(
            f"/documents/uploads/{document_upload_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            0,
            len(DocumentUpload.objects.filter(id=document_upload_id)),
        )

        response = self.student_president_client.delete(
            f"/documents/uploads/{document_upload_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
