"""List of tests done on projects views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate


class ProjectCommissionDateViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissiondate.json",
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "associations_association.json",
        "users_associationusers.json",
        "associations_activityfield.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "users_user.json",
        "account_emailaddress.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "users_groupinstitutioncommissionusers.json",
    ]

    def setUp(self):
        """Start a default anonymous client."""
        self.client = Client()
        url_login = reverse("rest_login")

        """ Start a manager general client used on a majority of tests. """
        self.manager_general_user_id = 3
        self.manager_general_user_name = "gestionnaire-svu@mail.tld"
        self.general_client = Client()
        data_general = {
            "username": self.manager_general_user_name,
            "password": "motdepasse",
        }
        self.response = self.general_client.post(url_login, data_general)

        """ Start a user misc that can submit personal projects. """
        self.student_misc_user_id = 9
        self.student_misc_user_name = "etudiant-porteur@mail.tld"
        self.student_misc_client = Client()
        data_student_misc = {
            "username": self.student_misc_user_name,
            "password": "motdepasse",
        }
        self.response = self.student_misc_client.post(url_login, data_student_misc)

    def test_get_project_cd_anonymous(self):
        """
        GET /projects/commission_dates .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_cd_search(self):
        """
        GET /projects/commission_dates? .

        - The route can be accessed by any authenticated user.
        - Correct search results are returned
        """
        project_id = 1
        search_db_count = len(
            ProjectCommissionDate.objects.filter(project_id=project_id)
        )
        response = self.general_client.get(
            f"/projects/commission_dates?project_id={project_id}"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(search_db_count, len(content))

    def test_post_project_cd_anonymous(self):
        """
        POST /projects/commission_dates .

        - An anonymous user cannot execute this request.
        """
        response = self.client.post(
            "/projects/commission_dates", {"project": 1, "commission_date": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_project_cd_bad_request(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by any authenticated user.
        - The attribute "amount_earned" is forbidden.
        """
        response = self.general_client.post(
            "/projects/commission_dates",
            {"project": 1, "commission_date": 1, "amount_earned": 1000},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cd_not_found(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by any authenticated user.
        - The project must be existing.
        """
        response = self.general_client.post(
            "/projects/commission_dates", {"project": 9999, "commission_date": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_cd_forbidden_user(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to edit the requested project.
        """
        response = self.general_client.post(
            "/projects/commission_dates", {"project": 1, "commission_date": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cd_user_success(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by any authenticated user.
        - The project must be existing.
        - The authenticated user must be authorized to edit the requested project.
        - Object is correctly created in db.
        """
        project_id = 1
        commission_id = 1
        post_data = {
            "project": project_id,
            "commission_date": commission_id,
            "amount_asked": 500,
        }
        response = self.student_misc_client.post(
            "/projects/commission_dates", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = ProjectCommissionDate.objects.filter(
            project_id=project_id, commission_date_id=commission_id
        )
        self.assertEqual(len(results), 1)

    def test_post_project_cd_already_exists(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by any authenticated user.
        - Request returns a status 201 the first time and a status 400 next.
        """
        project_id = 1
        commission_id = 2
        post_data = {
            "project": project_id,
            "commission_date": commission_id,
            "amount_asked": 500,
        }
        response = self.student_misc_client.post(
            "/projects/commission_dates", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_second = self.student_misc_client.post(
            "/projects/commission_dates", post_data
        )
        self.assertEqual(response_second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_project_cd_not_existing(self):
        """
        PUT /projects/commission_dates/{id} .

        - This route always returns a 404.
        """
        response = self.general_client.put(
            "/projects/commission_dates/1", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_cd_by_id_anonymous(self):
        """
        GET /projects/commission_dates/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/commission_dates/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_cd_anonymous(self):
        """
        PATCH /projects/commission_dates/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.patch(
            "/projects/commission_dates/1", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_cd_not_found(self):
        """
        PATCH /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - The ProjectCommissionDate object must be existing.
        """
        response = self.general_client.patch(
            "/projects/commission_dates/99999", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_cd_forbidden(self):
        """
        PATCH /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        """
        response = self.general_client.patch(
            "/projects/commission_dates/1", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cd_bad_request(self):
        """
        PATCH /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - The attributes to patch must be authorized.
        """
        response = self.student_misc_client.patch(
            "/projects/commission_dates/1",
            {"amount_earned": 1000},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_cd_bad_success(self):
        """
        PATCH /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - ProjectCommissionDate object is correctly updated.
        """
        pcd = 1
        patch_data = {"amount_asked": 1333}
        response = self.student_misc_client.patch(
            f"/projects/commission_dates/{pcd}",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pcd_data = ProjectCommissionDate.objects.get(pk=pcd)
        self.assertEqual(pcd_data.amount_asked, patch_data["amount_asked"])

    def test_delete_project_cd_anonymous(self):
        """
        DELETE /projects/commission_dates/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/commission_dates/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_cd_not_found(self):
        """
        DELETE /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - The ProjectCommissionDate object must be existing.
        """
        response = self.general_client.delete("/projects/commission_dates/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_cd_forbidden(self):
        """
        DELETE /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        """
        response = self.general_client.delete("/projects/commission_dates/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_cd_success(self):
        """
        DELETE /projects/commission_dates/{id} .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be authorized to update the project.
        - ProjectCommissionDate object is correctly removed from db.
        """
        pcd = 1
        response = self.student_misc_client.delete(f"/projects/commission_dates/{pcd}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        pcd_not_found = len(ProjectCommissionDate.objects.filter(pk=pcd))
        self.assertEqual(pcd_not_found, 0)
