"""List of tests done on documents views."""
import json
from unittest.mock import Mock

from django.core.files.storage import default_storage
from django.test import Client, TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework import status

from plana.apps.documents.models.document import Document
from plana.storages import DynamicStorageFieldFile


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
        "users_groupinstitutionfunduser.json",
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

        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

        cls.student_user_id = 9
        cls.student_user_name = "etudiant-porteur@mail.tld"
        cls.student_client = Client()
        data_student = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_client.post(url_login, data_student)

        document = Document.objects.create(
            name="Document factice d'établissement",
            description="Document factice d'établissement",
            institution_id=1,
            mime_types=["application/pdf", "image/jpeg", "image/png"],
        )
        cls.institution_document_id = document.id

    def test_get_documents_list(self):
        """
        GET /documents/ .

        - There's at least one document in the documents list.
        - The route can be accessed by anyone.
        - We get the same amount of documents through the model and through the view.
        - Documents details are returned (test the "name" attribute).
        - Filters by acronym and process type are available.
        """
        documents_cnt = Document.objects.count()
        self.assertTrue(documents_cnt > 0)

        response = self.client.get("/documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

        document_1 = content[0]
        self.assertTrue(document_1.get("name"))

        acronym = "CHARTE_SITE_ALSACE"
        response = self.client.get(f"/documents/?acronym={acronym}")
        self.assertEqual(response.data[0]["acronym"], acronym)

        process_types = ["DOCUMENT_PROJECT", "NO_PROCESS"]
        response = self.general_client.get(
            f"/documents/?process_types={','.join(str(x) for x in process_types)}"
        )
        documents_cnt = Document.objects.filter(process_type__in=process_types).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), documents_cnt)

    def test_post_documents_anonymous(self):
        """
        POST /documents/ .

        - An anonymous user can't execute this request.
        """
        post_data = {"name": "test anonymous"}
        response = self.client.post("/documents/", post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_documents_forbidden(self):
        """
        POST /documents/ .

        - A user without proper permissions can't execute this request.
        """
        post_data = {"name": "Test anonymous"}
        response = self.student_client.post("/documents/", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_documents_forbidden_institution(self):
        """
        POST /documents/ .

        - A user without access to requested institution can't execute this request.
        """
        institution = 1
        post_data = {"name": "Test forbidden", "institution": institution}
        response = self.institution_client.post("/documents/", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_documents_forbidden_commission(self):
        """
        POST /documents/ .

        - A user without access to requested commission can't execute this request.
        """
        commission = 3
        post_data = {"name": "Test forbidden", "commission": commission}
        response = self.institution_client.post("/documents/", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_documents_success(self):
        """
        POST /documents/ .

        - A user with proper permissions can execute this request.
        - Document object is successfully created in db.
        """
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()

        name = "Test success"
        post_data = {"name": name, "path_template": file}
        response = self.general_client.post("/documents/", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = Document.objects.filter(name=name)
        self.assertEqual(len(results), 1)

    def test_get_document_by_id_404(self):
        """
        GET /documents/{id} .

        - The route returns a 404 if a wrong document id is given.
        """
        response = self.general_client.get("/documents/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_put_document_by_id_405(self):
        """
        PUT /documents/{id} .

        - The route returns a 405 everytime.
        """
        data = {"name": "name"}
        response = self.general_client.put("/documents/1", data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_documents_anonymous(self):
        """
        PATCH /documents/{id} .

        - An anonymous user can't execute this request.
        """
        patch_data = {"name": "test anonymous"}
        response = self.client.patch(
            "/documents/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_documents_404(self):
        """
        PATCH /documents/{id} .

        - A user with proper permissions can execute this request.
        - Document must exist.
        """
        name = "Test fail"
        patch_data = {"name": name}
        response = self.general_client.patch(
            "/documents/999", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_documents_forbidden(self):
        """
        PATCH /documents/{id} .

        - A user without proper permissions can't execute this request.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.student_client.patch(
            "/documents/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_documents_forbidden_institution(self):
        """
        PATCH /documents/{id} .

        - A user without access to requested institution can't execute this request.
        """
        institution = 1
        patch_data = {"name": "Test forbidden", "institution": institution}
        response = self.institution_client.patch(
            f"/documents/{self.institution_document_id}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_documents_forbidden_commission(self):
        """
        PATCH /documents/{id} .

        - A user without access to requested commission can't execute this request.
        """
        commission = 3
        patch_data = {"name": "Test forbidden", "commission": commission}
        response = self.institution_client.patch(
            "/documents/3", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_documents_wrong_process(self):
        """
        PATCH /documents/{id} .

        - Document must have an updatable process type.
        """
        name = "Test process"
        patch_data = {"name": name}
        response = self.general_client.patch(
            "/documents/9", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_documents_success(self):
        """
        PATCH /documents/{id} .

        - A user with proper permissions can execute this request.
        - Returns 415 if MIME type is wrong.
        - Document object is successfully changed in db.
        """
        document_id = 1
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()

        name = "Test success"
        patch_data = encode_multipart(
            data={"name": name, "path_template": file},
            boundary=BOUNDARY,
        )
        response = self.general_client.patch(
            f"/documents/{document_id}", data=patch_data, content_type=MULTIPART_CONTENT
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        document = Document.objects.get(id=document_id)
        document.mime_types = [
            "application/vnd.novadigm.ext",
            "application/octet-stream",
        ]
        document.save()
        response = self.general_client.patch(
            f"/documents/{document_id}", data=patch_data, content_type=MULTIPART_CONTENT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = Document.objects.filter(name=name)
        self.assertEqual(len(results), 1)

    def test_delete_document_by_id_anonymous(self):
        """
        DELETE /documents/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/documents/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_document_by_id_404(self):
        """
        DELETE /documents/{id} .

        - The route returns a 404 if a wrong document id is given.
        """
        response = self.general_client.delete("/documents/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_document_by_id_forbidden_institution(self):
        """
        DELETE /documents/{id} .

        - A document linked to an institution cannot be deleted by a user who's not linked to the same institution.
        """
        document_id = 25
        response = self.institution_client.delete(f"/documents/{document_id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_document_by_id_forbidden_commission(self):
        """
        DELETE /documents/{id} .

        - A document linked to a commission cannot be deleted by a user who's not linked to the same commission.
        """
        document_id = 7
        response = self.institution_client.delete(f"/documents/{document_id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_document_wrong_process(self):
        """
        DELETE /documents/{id} .

        - Document must have an updatable process type.
        """
        response = self.general_client.delete("/documents/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_document_by_id(self):
        """
        DELETE /documents/{id} .

        - The route can be accessed by an authenticated user with correct permissions.
        - The document is correctly deleted.
        """
        response = self.general_client.delete(
            f"/documents/{self.institution_document_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        doc_deleted = Document.objects.filter(id=self.institution_document_id)
        self.assertEqual(len(doc_deleted), 0)
