"""List of tests done on links between projects and commission dates views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate


class ProjectCommissionDateViewsTests(TestCase):
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
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissiondate.json",
        "users_associationusers.json",
        "users_groupinstitutioncommissionusers.json",
        "users_user.json",
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

    def test_get_project_cd_student(self):
        """
        GET /projects/commission_dates .

        - A student user gets commission dates details where projects rights are OK.
        """
        response = self.student_misc_client.get("/projects/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_cd_search(self):
        """
        GET /projects/commission_dates .

        - The route can be accessed by a manager user.
        - Correct search results are returned.
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

        commission_id = 1
        search_db_count = len(
            ProjectCommissionDate.objects.filter(
                commission_date_id__in=CommissionDate.objects.filter(
                    commission_id=commission_id
                )
            )
        )
        response = self.general_client.get(
            f"/projects/commission_dates?commission_id={commission_id}"
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

        - The route can be accessed by a student user.
        - The attribute "amount_earned" is restricted.
        """
        response = self.student_misc_client.post(
            "/projects/commission_dates",
            {"project": 1, "commission_date": 1, "amount_earned": 1000},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cd_not_found(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The project must be existing.
        """
        response = self.student_misc_client.post(
            "/projects/commission_dates", {"project": 9999, "commission_date": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_cd_forbidden_user(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The authenticated user must be authorized to edit the requested project.
        """
        response = self.student_misc_client.post(
            "/projects/commission_dates", {"project": 2, "commission_date": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cd_wrong_submission_date(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The commission submission date must not be over.
        """
        commission_date_id = 1
        commission_date = CommissionDate.objects.get(pk=commission_date_id)
        commission_date.submission_date = "1968-05-03"
        commission_date.save()
        response = self.student_misc_client.post(
            "/projects/commission_dates",
            {"project": 1, "commission_date": commission_date_id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cd_user_success(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
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

        - The route can be accessed by a student user.
        - Request returns a status 201 the first time and a status 200 next.
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
        self.assertEqual(response_second.status_code, status.HTTP_200_OK)

    def test_put_project_cd_not_existing(self):
        """
        PUT /projects/{project_id}/commission_dates .

        - This route always returns a 405.
        """
        response = self.student_misc_client.put(
            "/projects/1/commission_dates", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_project_cd_by_id_anonymous(self):
        """
        GET /projects/{project_id}/commission_dates .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_cd_by_id_forbidden_student(self):
        """
        GET /projects/{project_id}/commission_dates .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_misc_client.get("/projects/2/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_cd_by_id_manager(self):
        """
        GET /projects/{project_id}/commission_dates .

        - The route can be accessed by a manager user.
        - Correct projects categories are returned.
        """
        project_id = 1
        project_test_cnt = ProjectCommissionDate.objects.filter(
            project_id=project_id
        ).count()
        response = self.general_client.get(f"/projects/{project_id}/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

    def test_get_project_cd_by_id_404(self):
        """
        GET /projects/{project_id}/categories .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_cd(self):
        """
        GET /projects/{project_id}/commission_dates/{commission_date_id} .

        - Always returns a 405.
        """
        response = self.general_client.get("/projects/1/commission_dates/3")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_project_cd(self):
        """
        PUT /projects/{project_id}/commission_dates/{commission_date_id} .

        - Always returns a 405.
        """
        response = self.general_client.put(
            "/projects/1/commission_dates/3", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_cd_anonymous(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.patch(
            "/projects/1/commission_dates/3", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_cd_not_found(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by a student user.
        - The ProjectCommissionDate object must be existing.
        """
        response = self.student_misc_client.patch(
            "/projects/99999/commission_dates/99999",
            {},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_cd_forbidden_student(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by a student.
        - The student must be authorized to update the project commission dates.
        """
        response = self.student_misc_client.patch(
            "/projects/2/commission_dates/1", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cd_forbidden_manager(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by a manager.
        - The manager must be authorized to update project commission dates basic fields.
        """
        response = self.general_client.patch(
            "/projects/2/commission_dates/1", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cd_bad_request(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by any authenticated user.
        - The attributes to patch must be authorized.
        """
        response = self.student_misc_client.patch(
            "/projects/1/commission_dates/3",
            {"amount_earned": 1000},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cd_wrong_submission_date(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by any authenticated user.
        - The commission submission date must not be over.
        """
        commission_date_id = 3
        commission_date = CommissionDate.objects.get(pk=commission_date_id)
        commission_date.submission_date = "1968-05-03"
        commission_date.save()
        response = self.student_misc_client.patch(
            f"/projects/1/commission_dates/{commission_date_id}",
            {"amount_asked": 1333},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_cd_success(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by any authenticated user.
        - ProjectCommissionDate object is correctly updated.
        """
        patch_data = {"amount_asked": 1333}
        response = self.student_misc_client.patch(
            "/projects/1/commission_dates/3",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pcd_data = ProjectCommissionDate.objects.get(project_id=1, commission_date_id=3)
        self.assertEqual(pcd_data.amount_asked, patch_data["amount_asked"])

    def test_delete_project_cd_anonymous(self):
        """
        DELETE /projects/{project_id}/commission_dates/{commission_date_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/1/commission_dates/3")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_cd_not_found(self):
        """
        DELETE /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by a student client.
        - The ProjectCommissionDate object must exist.
        """
        response = self.student_misc_client.delete(
            "/projects/99999/commission_dates/99999"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_cd_forbidden(self):
        """
        DELETE /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by a student user.
        - The authenticated user must be authorized to update the project commission dates.
        """
        response = self.student_misc_client.delete("/projects/2/commission_dates/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_cd_success(self):
        """
        DELETE /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by a student user.
        - The authenticated user must be authorized to update the project commission dates.
        - ProjectCommissionDate object is correctly removed from db.
        """
        response = self.student_misc_client.delete("/projects/1/commission_dates/3")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        pcd_not_found = len(
            ProjectCommissionDate.objects.filter(project_id=1, commission_date_id=3)
        )
        self.assertEqual(pcd_not_found, 0)
