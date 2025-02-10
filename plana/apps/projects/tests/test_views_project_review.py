"""List of tests done on project reviews views."""

import datetime
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.commissions.models.commission import Commission
from plana.apps.projects.models.project import Project


class ProjectReviewsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_fund.json",
        "commissions_commission.json",
        "commissions_commissionfund.json",
        "contents_setting.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissionfund.json",
        "users_associationuser.json",
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
        cls.response = cls.student_president_client.post(url_login, data_student_president)

    def test_get_project_review_by_id_anonymous(self):
        """
        GET /projects/{id}/review .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/5/review")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_review_by_id_404(self):
        """
        GET /projects/{id}/review .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/review")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_review_by_id_forbidden_student(self):
        """
        GET /projects/{id}/review .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.get("/projects/6/review")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_review_by_id(self):
        """
        GET /projects/{id}/review .

        - The route can be accessed by a manager user.
        - The route can be accessed by a student user.
        - Correct projects details are returned (test the "name" attribute).
        """
        project_id = 5
        project_test = Project.visible_objects.get(id=project_id)
        response = self.general_client.get(f"/projects/{project_id}/review")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["name"], project_test.name)

        project_id = 6
        project_test = Project.visible_objects.get(id=project_id)
        response = self.student_president_client.get(f"/projects/{project_id}/review")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["name"], project_test.name)

    def test_patch_project_review_anonymous(self):
        """
        PATCH /projects/{id}/review .

        - An anonymous user cannot execute this request.
        """
        patch_data = {"review": "C'était bien"}
        response = self.client.patch("/projects/5/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_review_not_found(self):
        """
        PATCH /projects/{id}/review .

        - The route can be accessed by a student user.
        - Project must exist.
        """
        patch_data = {"review": "C'était pas ouf"}
        response = self.student_misc_client.patch("/projects/999/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_review_forbidden_student(self):
        """
        PATCH /projects/{id}/review .

        - An student user not owning the project cannot execute this request.
        """
        patch_data = {"review": "C'était moyen"}
        response = self.student_offsite_client.patch("/projects/6/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_review_forbidden_user(self):
        """
        PATCH /projects/{id}/review .

        - The route can be accessed by a student user.
        - The project owner must be the authenticated user.
        """
        patch_data = {"review": "Du pur génie, 9 sélec sur Gamekult"}
        response = self.student_site_client.patch("/projects/5/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_review_manager_error(self):
        """
        PATCH /projects/{id}/review .

        - The route cannot be accessed by a manager user.
        """
        patch_data = {"review": "Mon chien aurait fait mieux"}
        response = self.general_client.patch("/projects/6/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_review_user_wrong_status(self):
        """
        PATCH /projects/{id}/review .

        - The route can be accessed by a student user.
        - Status must be draft.
        """
        patch_data = {"review": "J'ai montré ma recette à un cuisinier, il m'a fait bouffer l'assiette."}
        response = self.student_misc_client.patch("/projects/7/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_review_association_wrong_dates(self):
        """
        PATCH /projects/{id}/review .

        - The route can be accessed by a student user.
        - Real start date cannot be set after real end date.
        """
        project_data = {
            "real_start_date": "2099-12-25T14:00:00.000Z",
            "real_end_date": "2099-11-30T18:00:00.000Z",
        }
        response = self.student_president_client.patch(
            "/projects/6/review", project_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_review_serializer_error(self):
        """
        PATCH /projects/{id}/review .

        - The route can be accessed by a student user.
        - Serializer fields must be valid.
        """
        patch_data = {"review": False}
        response = self.student_misc_client.patch("/projects/5/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_review_user_success(self):
        """
        PATCH /projects/{id}/review .

        - The route can be accessed by a student user.
        - The project is correctly updated in db.
        """
        patch_data = {"review": "J'ai montré ma recette à un cuisinier, il m'a fait bouffer l'assiette."}
        response = self.student_misc_client.patch("/projects/5/review", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=5)
        self.assertEqual(project.review, patch_data["review"])
