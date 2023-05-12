"""List of tests done on links between projects and commission dates views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.users.models.user import GroupInstitutionCommissionUser


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
        "projects_project.json",
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

        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"
        cls.president_student_client = Client()
        url = reverse("rest_login")
        data = {
            "username": cls.president_user_name,
            "password": "motdepasse",
        }
        cls.response_president = cls.president_student_client.post(url, data)

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

    def test_get_project_cd_manager(self):
        """
        GET /projects/commission_dates .

        - A student user gets commission dates details where projects rights are OK.
        """
        response = self.institution_client.get("/projects/commission_dates")
        user_institutions_ids = Institution.objects.filter(
            id__in=GroupInstitutionCommissionUser.objects.filter(
                user_id=self.manager_institution_user_id
            ).values_list("institution_id")
        )
        pcd_cnt = ProjectCommissionDate.objects.filter(
            project_id__in=Project.objects.filter(
                association_id__in=Association.objects.filter(
                    institution_id__in=user_institutions_ids
                ).values_list("id")
            )
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), pcd_cnt)

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

    def test_post_project_cd_not_found(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The project must exist.
        """
        response = self.student_misc_client.post(
            "/projects/commission_dates", {"project": 9999, "commission_date": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_cd_manager_bad_request(self):
        """
        POST /projects/commission_dates .

        - The route cannot be accessed by a manager user.
        """
        response = self.general_client.post("/projects/commission_dates", {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cd_student_bad_request(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The attribute "amount_earned" is restricted for students.
        """
        response = self.student_misc_client.post(
            "/projects/commission_dates",
            {"project": 1, "commission_date": 1, "amount_earned": 1000},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_post_project_cd_user_not_site(self):
        """
        POST /projects/commission_dates .

        - A misc student cannot submit a project to a is_site commission.
        """
        project_id = 1
        commission_date_id = 2
        post_data = {
            "project": project_id,
            "commission_date": commission_date_id,
            "amount_asked": 500,
        }
        response = self.student_misc_client.post(
            "/projects/commission_dates", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cd_wrong_submission_date(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The commission submission date must not be over.
        """
        commission_date_id = 5
        commission_date = CommissionDate.objects.get(id=commission_date_id)
        commission_date.submission_date = "1968-05-03"
        commission_date.save()
        response = self.student_misc_client.post(
            "/projects/commission_dates",
            {"project": 1, "commission_date": commission_date_id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cd_not_next_commission(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - A project can only be submitted to the first date for a commission.
        """
        response = self.student_misc_client.post(
            "/projects/commission_dates",
            {"project": 1, "commission_date": 5},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cd_commission_already_used(self):
        """
        POST /projects/commission_dates .

        - A student cannot submit a same project twice in the same commission.
        """
        project_id = 1
        commission_date_id = 3
        post_data = {
            "project": project_id,
            "commission_date": commission_date_id,
        }
        response = self.student_misc_client.post(
            "/projects/commission_dates", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cd_user_success(self):
        """
        POST /projects/commission_dates .

        - The route can be accessed by a student user.
        - The project must exist.
        - The authenticated user must be authorized to edit the requested project.
        - Object is correctly created in db.
        """
        project_id = 2
        commission_date_id = 3
        ProjectCommissionDate.objects.get(
            project_id=project_id, commission_date_id=4
        ).delete()
        post_data = {
            "project": project_id,
            "commission_date": commission_date_id,
            "amount_asked": 500,
        }
        response = self.president_student_client.post(
            "/projects/commission_dates", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = ProjectCommissionDate.objects.filter(
            project_id=project_id, commission_date_id=commission_date_id
        )
        self.assertEqual(len(results), 1)

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

    def test_get_project_cd_by_id_404(self):
        """
        GET /projects/{project_id}/categories .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        - The route can be accessed by a student user.
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

        project_id = 2
        project_test_cnt = ProjectCommissionDate.objects.filter(
            project_id=project_id
        ).count()
        response = self.president_student_client.get(
            f"/projects/{project_id}/commission_dates"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

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
        - The ProjectCommissionDate object must exist.
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
            "/projects/2/commission_dates/4", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cd_student_bad_request(self):
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

    def test_patch_project_cd_manager_bad_request(self):
        """
        PATCH /projects/{project_id}/commission_dates/{commission_date_id} .

        - The route can be accessed by any authenticated user.
        - The attributes to patch must be authorized.
        """
        response = self.general_client.patch(
            "/projects/1/commission_dates/3",
            {"amount_asked": 1000},
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
        commission_date = CommissionDate.objects.get(id=commission_date_id)
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
        response = self.student_misc_client.delete("/projects/2/commission_dates/4")
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
