"""List of tests done on association exports views."""
import csv
import io
import json
from unittest.mock import Mock

from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.test import Client, TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.users.models.user import AssociationUser
from plana.storages import DynamicThumbnailImageField


class AssociationExportsViewsTests(TestCase):
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
        "users_user.json",
        "users_groupinstitutionfunduser.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on all tests."""
        cls.client = Client()
        url_login = reverse("rest_login")

        # Start a student member of an association client used in some tests
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.member_client = Client()
        data_member = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.member_client.post(url_login, data_member)

        # Start a student president of an association client used in some tests
        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"
        cls.president_client = Client()
        data_president = {
            "username": cls.president_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.president_client.post(url_login, data_president)

        # Start a manager institution client used in some tests
        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

        # Start a manager general client used in some tests
        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.general_client = Client()
        data_general = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.general_client.post(url_login, data_general)

    def test_get_pdf_export_association_by_id_anonymous(self):
        """
        GET /associations/{id}/export .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/associations/2/export")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_pdf_export_association_by_id_404(self):
        """
        GET /associations/{id}/export .

        - The route returns a 404 if a wrong association id is given.
        """
        response = self.general_client.get("/associations/99999/export")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_pdf_export_association_by_id_forbidden_student(self):
        """
        GET /associations/{id}/export .

        - An student user not president cannot execute this request.
        """
        response = self.member_client.get("/associations/2/export")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_pdf_export_association_by_id(self):
        """
        GET /associations/{id}/export .

        - The route can be accessed by a manager user.
        - The route can be accessed by a president user.
        """
        association_id = 2
        response = self.general_client.get(f"/associations/{association_id}/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.president_client.get(f"/associations/{association_id}/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_csv_export_associations_success_general_manager(self):
        """
        GET /associations/csv_export .

        - The route can be accessed by a manager user.
        - All associations from db are returned in the CSV.
        """
        response = self.general_client.get(f"/associations/csv_export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        total = Association.objects.all().count()
        # -1 because of CSV header
        self.assertEqual(len(list(csv_reader)) - 1, total)

    def test_get_csv_export_associations_filtered_general_manager(self):
        """
        GET /associations/csv_export .

        - The route can be accessed by a manager user.
        - All selected associations from db are returned in the CSV.
        """
        response = self.general_client.get(
            f"/associations/csv_export?associations=1,2,3"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        total = Association.objects.filter(id__in=[1, 2, 3]).count()
        # -1 because of CSV header
        self.assertEqual(len(list(csv_reader)) - 1, total)


# TODO : unittests for permissions, institutions check in CSV export
