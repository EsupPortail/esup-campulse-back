"""List of tests done on project PDF generation."""
import json
from unittest.mock import Mock

from django.core import mail
from django.core.files.storage import default_storage
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.institutions.models import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.users.models.user import AssociationUser, GroupInstitutionCommissionUser
from plana.storages import DynamicStorageFieldFile


class ProjectsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissiondate.json",
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

        cls.student_offsite_user_id = 10
        cls.student_offsite_user_name = "etudiant-asso-hors-site@mail.tld"
        cls.student_offsite_client = Client()
        data_student_offsite = {
            "username": cls.student_offsite_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_offsite_client.post(url_login, data_student_offsite)

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

        project_id = 1
        DocumentUpload.objects.filter(project_id=project_id).delete()
        document_id = 18
        field = Mock()
        field.storage = default_storage
        file = DynamicStorageFieldFile(Mock(), field=field, name="filename.ext")
        file.storage = Mock()
        post_data = {
            "path_file": file,
            "project": project_id,
            "document": document_id,
            "user": cls.student_misc_user_id,
        }
        document = Document.objects.get(id=document_id)
        document.mime_types = [
            "application/vnd.novadigm.ext",
            "application/octet-stream",
        ]
        document.save()
        cls.new_document = cls.student_misc_client.post("/documents/uploads", post_data)

    def test_get_export_project_by_id_anonymous(self):
        """
        GET /projects/{id}/export .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1/export")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_export_project_by_id_404(self):
        """
        GET /projects/{id}/export .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/export")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_export_project_by_id_forbidden_student(self):
        """
        GET /projects/{id}/export .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.get("/projects/1/export")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_export_project_by_id(self):
        """
        GET /projects/{id}/export .

        - The route can be accessed by a manager user.
        - The route can be accessed by a student user.
        """
        project_id = 3
        response = self.general_client.get(f"/projects/{project_id}/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        project_id = 2
        response = self.student_president_client.get(f"/projects/{project_id}/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
