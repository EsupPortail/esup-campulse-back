"""List of tests done on documents views."""
import json
from unittest.mock import Mock

from django.core import mail
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
        "commissions_fund.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "users_associationuser.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start clients used on tests, and post a fake document for GET routes."""
        cls.client = Client()
        url_login = reverse("rest_login")

        cls.unvalidated_user_id = 2
        cls.unvalidated_user_name = "compte-non-valide@mail.tld"

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

        documents = Document.objects.filter(id__in=[18, 21])
        documents.update(
            mime_types=[
                "application/vnd.novadigm.ext",
                "application/octet-stream",
            ]
        )
        for document in documents:
            document.save()
        DocumentUpload.objects.filter(project_id__in=[1, 5]).delete()
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()
        post_data_1 = {
            "path_file": file,
            "project": 1,
            "document": 18,
            "user": cls.student_misc_user_id,
        }
        post_data_2 = {
            "path_file": file,
            "project": 5,
            "document": 21,
            "user": cls.student_misc_user_id,
        }
        cls.student_misc_client.post("/documents/uploads", post_data_1)
        cls.new_document = cls.student_misc_client.post(
            "/documents/uploads", post_data_2
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
        - user, association, project and process_types filters work.
        """
        DocumentUpload.objects.exclude(id=self.new_document.data["id"]).delete()
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

        document_statuses = ["CHARTER_DRAFT", "CHARTER_PROCESSING"]
        response = self.general_client.get(
            f"/documents/uploads?process_types={','.join(str(x) for x in document_statuses)}"
        )
        documents_cnt = DocumentUpload.objects.filter(project_id=project_id).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

        response = self.general_client.get(
            "/documents/uploads?is_validated_by_admin=true"
        )
        documents_cnt = DocumentUpload.objects.exclude(
            validated_date__isnull=True
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

    def test_post_document_upload_project_anonymous(self):
        """
        POST /documents/uploads .
        - An anonymous user can execute this request.
        - project and association cannot be specified.
        - Document must have a DOCUMENT_USER process type.
        """
        post_data = {
            "path_file": "",
            "project": 1,
            "document": 16,
        }
        response = self.client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        post_data = {
            "path_file": "",
            "user": self.unvalidated_user_id,
            "document": 16,
        }
        response = self.client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        document_id = 14
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()
        document = Document.objects.get(id=document_id)
        document.mime_types = [
            "application/vnd.novadigm.ext",
            "application/octet-stream",
        ]
        document.save()
        post_data = {
            "path_file": file,
            "user": self.unvalidated_user_id,
            "document": document_id,
        }
        response = self.client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_document_upload_project_not_found(self):
        """
        POST /documents/uploads .
        - The route can be accessed by any authenticated user.
        - The project edited must exist.
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
        - The document linked must exist.
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
        response = self.student_site_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_document_upload_bad_request(self):
        """
        POST /documents/uploads .

        - The route can be accessed by a student user.
        - Document must have at least one affectation (user or association).
        - If linked to an association, the association must already exist.
        - If linked to a user, the user must already exist.
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

        document_data.pop("association", None)
        document_data["user"] = 9999
        response = self.student_site_client.post("/documents/uploads", document_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        document_data["association"] = 2
        document_data["user"] = self.student_president_user_id
        response = self.student_president_client.post(
            "/documents/uploads", document_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_document_upload_serializer_error(self):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - Serializer fields must be valid.
        """
        project_id = 1
        document_id = 19
        post_data = {
            "path_file": False,
            "project": project_id,
            "document": document_id,
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post(
            "/documents/uploads", data=post_data, content_type="application/json"
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
        - Object is not created if field is not is_multiple.
        """
        post_data = {
            "path_file": "",
            "project": 1,
            "document": 18,
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_document_upload_validated(self):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        - Object is not created if validation is set by a student.
        """
        post_data = {
            "path_file": "",
            "project": 1,
            "document": 19,
            "user": self.student_misc_user_id,
            "validated_date": "2023-03-15",
        }
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_document_upload_project_success(self):
        """
        POST /documents/uploads .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        - Returns 415 if MIME type is wrong.
        - Object is correctly created in db.
        """
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()

        project_id = 1
        document_id = 19
        post_data = {
            "path_file": file,
            "project": project_id,
            "document": document_id,
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        document = Document.objects.filter(id__in=[3, 19])
        document.update(
            mime_types=[
                "application/vnd.novadigm.ext",
                "application/octet-stream",
            ]
        )

        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        du_cnt = len(
            DocumentUpload.objects.filter(
                project_id=project_id, document_id=document_id
            )
        )
        self.assertEqual(du_cnt, 1)

        self.assertFalse(len(mail.outbox))
        post_data["document"] = 3
        post_data.pop("project", None)
        response = self.student_misc_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        du_cnt = len(
            DocumentUpload.objects.filter(
                user_id=post_data["user"], document_id=post_data["document"]
            ),
        )
        self.assertEqual(du_cnt, 1)
        self.assertTrue(len(mail.outbox))

        post_data["association"] = 2
        document_upload = DocumentUpload.objects.get(
            association_id=post_data["association"], document_id=post_data["document"]
        )
        document_upload.delete()
        post_data.pop("user", None)
        response = self.student_president_client.post("/documents/uploads", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        du_cnt = len(
            DocumentUpload.objects.filter(
                association_id=post_data["association"],
                document_id=post_data["document"],
            ),
        )
        self.assertEqual(du_cnt, 1)

    def test_get_document_upload_by_id_anonymous(self):
        """
        GET /documents/uploads/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/documents/uploads/2")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_document_upload_by_id_404(self):
        """
        GET /documents/uploads/{id} .

        - The route returns a 404 if a wrong document upload id is given.
        """
        response = self.general_client.get("/documents/uploads/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        - The route can be accessed by a student user.
        """
        response = self.student_misc_client.get(
            f"/documents/uploads/{self.new_document.data['id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_document_upload_by_id_405(self):
        """
        PUT /documents/uploads/{id} .

        - The route returns a 405 everytime.
        """
        data = {"is_validated_by_admin": True}
        response = self.general_client.put(
            f"/documents/uploads/{self.new_document.data['id']}", data
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_document_upload_anonymous(self):
        """
        PATCH /documents/uploads/{id} .

        - An anonymous user can't execute this request.
        """
        patch_data = {"validated_date": "2023-03-15"}
        response = self.client.patch(
            f"/documents/uploads/{self.new_document.data['id']}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_document_upload_404(self):
        """
        PATCH /documents/uploads/{id} .

        - A user with proper permissions can execute this request.
        - Document Upload must exist.
        """
        patch_data = {"validated_date": "2023-03-15"}
        response = self.general_client.patch(
            "/documents/uploads/999", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_document_upload_forbidden(self):
        """
        PATCH /documents/uploads/{id} .

        - A user without proper permissions can't execute this request.
        """
        patch_data = {"validated_date": "2023-03-15"}
        response = self.student_site_client.patch(
            f"/documents/uploads/{self.new_document.data['id']}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_document_upload_forbidden_institution(self):
        """
        PATCH /documents/uploads/{id} .

        - A user without access to requested institution can't execute this request.
        """
        document = Document.objects.get(id=self.new_document.data["document"])
        document.institution_id = 7
        document.save()
        patch_data = {"validated_date": "2023-03-15"}
        response = self.institution_client.patch(
            f"/documents/uploads/{self.new_document.data['id']}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_document_upload_forbidden_fund(self):
        """
        PATCH /documents/uploads/{id} .

        - A user without access to requested fund can't execute this request.
        """
        document = Document.objects.get(id=self.new_document.data["document"])
        document.fund_id = 1
        document.save()
        patch_data = {"validated_date": "2023-03-15"}
        response = self.institution_client.patch(
            f"/documents/uploads/{self.new_document.data['id']}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_documents_serializer_error(self):
        """
        PATCH /documents/uploads/{id} .

        - A user with proper permissions can execute this request.
        - Serializers fields must be valid.
        """
        patch_data = {"validated_date": "saucisse"}
        response = self.general_client.patch(
            f"/documents/uploads/{self.new_document.data['id']}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_documents_success(self):
        """
        PATCH /documents/uploads/{id} .

        - A user with proper permissions can execute this request.
        - Document object is successfully changed in db.
        """
        self.assertFalse(len(mail.outbox))
        patch_data = {"validated_date": "2023-03-15"}
        response = self.general_client.patch(
            f"/documents/uploads/{self.new_document.data['id']}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(mail.outbox))

        document_upload = DocumentUpload.objects.get(id=self.new_document.data['id'])
        self.assertNotEqual(document_upload.validated_date, None)

        response = self.general_client.patch(
            "/documents/uploads/6",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        document_upload = DocumentUpload.objects.get(id=6)
        self.assertNotEqual(document_upload.validated_date, None)

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
        - The document upload must exist.
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
        - The route can be accessed by a manager user.
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

        self.assertFalse(len(mail.outbox))
        response = self.general_client.delete("/documents/uploads/7")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(len(mail.outbox))

        response = self.general_client.delete(
            f"/documents/uploads/{self.new_document.data['id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_document_upload_file_by_id_anonymous(self):
        """
        GET /documents/uploads/{id}/file .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/documents/uploads/2/file")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_document_upload_file_by_id_404(self):
        """
        GET /documents/uploads/{id}/file .

        - The route returns a 404 if a wrong document upload id is given.
        """
        response = self.general_client.get("/documents/uploads/99999/file")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_document_upload_file_by_id_forbidden_student(self):
        """
        GET /documents/uploads/{id}/file .

        - An student user not owning the document cannot execute this request.
        """
        response = self.student_misc_client.get("/documents/uploads/6/file")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_document_upload_file_by_id(self):
        """
        GET /documents/uploads/{id}/file .

        - The route can be accessed by a student user.
        """
        response = self.student_misc_client.get(
            f"/documents/uploads/{self.new_document.data['id']}/file"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
