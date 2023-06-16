"""List of tests done on links between projects and commission funds views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import Commission, CommissionFund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.users.models.user import GroupInstitutionFundUser


class ProjectCommissionFundViewsTests(TestCase):
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
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
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

    def test_get_project_cf_anonymous(self):
        """
        GET /projects/commission_funds .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/commission_funds")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_cf_student(self):
        """
        GET /projects/commission_funds .

        - A student user gets commission funds details where projects rights are OK.
        """
        response = self.student_misc_client.get("/projects/commission_funds")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_cf_manager(self):
        """
        GET /projects/commission_funds .

        - A student user gets commission funds details where projects rights are OK.
        """
        response = self.institution_client.get("/projects/commission_funds")
        user_institutions_ids = Institution.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(
                user_id=self.manager_institution_user_id
            ).values_list("institution_id")
        )
        pcf_cnt = ProjectCommissionFund.objects.filter(
            project_id__in=Project.visible_objects.filter(
                association_id__in=Association.objects.filter(
                    institution_id__in=user_institutions_ids
                ).values_list("id")
            )
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), pcf_cnt)

    def test_get_project_cf_search(self):
        """
        GET /projects/commission_funds .

        - The route can be accessed by a manager user.
        - Correct search results are returned.
        """
        project_id = 1
        search_db_count = len(
            ProjectCommissionFund.objects.filter(project_id=project_id)
        )
        response = self.general_client.get(
            f"/projects/commission_funds?project_id={project_id}"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(search_db_count, len(content))

        commission_id = 1
        search_db_count = len(
            ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                )
            )
        )
        response = self.general_client.get(
            f"/projects/commission_funds?commission_id={commission_id}"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(search_db_count, len(content))

    def test_post_project_cf_anonymous(self):
        """
        POST /projects/commission_funds .

        - An anonymous user cannot execute this request.
        """
        response = self.client.post(
            "/projects/commission_funds", {"project": 1, "commission_fund": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_project_cf_not_found(self):
        """
        POST /projects/commission_funds .

        - The route can be accessed by a student user.
        - The project must exist.
        """
        response = self.student_misc_client.post(
            "/projects/commission_funds", {"project": 9999, "commission_fund": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_cf_serializer_error(self):
        """
        POST /projects/commission_funds .

        - If data format is not good we get a bad request from the serializer.
        """
        post_data = {"project": 1, "commission_fund": 1, "amount_asked": True}
        response = self.student_misc_client.post(
            "/projects/commission_funds", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cf_manager_forbidden(self):
        """
        POST /projects/commission_funds .

        - The route cannot be accessed by a manager user.
        """
        response = self.general_client.post("/projects/commission_funds", {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cf_student_bad_request(self):
        """
        POST /projects/commission_funds .

        - The route can be accessed by a student user.
        - The attribute "amount_earned" is restricted for students.
        """
        response = self.student_misc_client.post(
            "/projects/commission_funds",
            {"project": 1, "commission_fund": 1, "amount_earned": 1000},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cf_forbidden_user(self):
        """
        POST /projects/commission_funds .

        - The route can be accessed by a student user.
        - The authenticated user must be authorized to edit the requested project.
        """
        response = self.student_misc_client.post(
            "/projects/commission_funds", {"project": 2, "commission_fund": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cf_user_not_site(self):
        """
        POST /projects/commission_funds .

        - A misc student cannot submit a project to a is_site fund.
        """
        project_id = 1
        commission_fund_id = 2
        post_data = {
            "project": project_id,
            "commission_fund": commission_fund_id,
            "amount_asked": 500,
        }
        response = self.student_misc_client.post(
            "/projects/commission_funds", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_cf_wrong_submission_date(self):
        """
        POST /projects/commission_funds .

        - The route can be accessed by a student user.
        - The commission submission date must not be over.
        """
        commission_fund_id = 6
        response = self.student_misc_client.post(
            "/projects/commission_funds",
            {"project": 1, "commission_fund": commission_fund_id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cf_not_open_to_projects(self):
        """
        POST /projects/commission_funds .

        - The route can be accessed by a student user.
        - The commission must be open.
        """
        commission = Commission.objects.get(id=3)
        commission.is_open_to_projects = False
        commission.save()
        commission_fund_id = 5
        response = self.student_misc_client.post(
            "/projects/commission_funds",
            {"project": 1, "commission_fund": commission_fund_id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cf_already_exists(self):
        """
        POST /projects/commission_funds .

        - A project cannot be linked twice to the same commission fund.
        """
        post_data = {"project": 1, "commission_fund": 3}
        response = self.student_misc_client.post(
            "/projects/commission_funds", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cf_multiple_commissions(self):
        """
        POST /projects/commission_funds .

        - A student cannot submit a same project to multiple commissions.
        """
        project_id = 2
        commission_fund_id = 4
        post_data = {
            "project": project_id,
            "commission_fund": commission_fund_id,
        }
        response = self.president_student_client.post(
            "/projects/commission_funds", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_cf_user_success(self):
        """
        POST /projects/commission_funds .

        - The route can be accessed by a student user.
        - The project must exist.
        - The authenticated user must be authorized to edit the requested project.
        - Object is correctly created in db.
        """
        project_id = 1
        commission_fund_id = 3
        ProjectCommissionFund.objects.get(
            project_id=project_id, commission_fund_id=commission_fund_id
        ).delete()
        post_data = {
            "project": project_id,
            "commission_fund": commission_fund_id,
            "amount_asked": 500,
        }
        response = self.student_misc_client.post(
            "/projects/commission_funds", post_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = ProjectCommissionFund.objects.filter(
            project_id=project_id, commission_fund_id=commission_fund_id
        )
        self.assertEqual(len(results), 1)

    def test_put_project_cf_not_existing(self):
        """
        PUT /projects/{project_id}/commission_funds .

        - This route always returns a 405.
        """
        response = self.student_misc_client.put(
            "/projects/1/commission_funds", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_project_cf_by_id_anonymous(self):
        """
        GET /projects/{project_id}/commission_funds .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1/commission_funds")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_cf_by_id_404(self):
        """
        GET /projects/{project_id}/categories .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/commission_funds")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_cf_by_id_forbidden_student(self):
        """
        GET /projects/{project_id}/commission_funds .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_misc_client.get("/projects/2/commission_funds")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_cf_by_id_manager(self):
        """
        GET /projects/{project_id}/commission_funds .

        - The route can be accessed by a manager user.
        - The route can be accessed by a student user.
        - Correct projects categories are returned.
        """
        project_id = 1
        project_test_cnt = ProjectCommissionFund.objects.filter(
            project_id=project_id
        ).count()
        response = self.general_client.get(f"/projects/{project_id}/commission_funds")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

        project_id = 2
        project_test_cnt = ProjectCommissionFund.objects.filter(
            project_id=project_id
        ).count()
        response = self.president_student_client.get(
            f"/projects/{project_id}/commission_funds"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

    def test_get_project_cf(self):
        """
        GET /projects/{project_id}/commission_funds/{commission_fund_id} .

        - Always returns a 405.
        """
        response = self.general_client.get("/projects/1/commission_funds/3")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_project_cf(self):
        """
        PUT /projects/{project_id}/commission_funds/{commission_fund_id} .

        - Always returns a 405.
        """
        response = self.general_client.put(
            "/projects/1/commission_funds/3", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_cf_anonymous(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.patch(
            "/projects/1/commission_funds/3", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_cf_not_found(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by a student user.
        - The ProjectCommissionFund object must exist.
        """
        response = self.student_misc_client.patch(
            "/projects/99999/commission_funds/99999",
            {},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_cf_forbidden_student(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by a student.
        - The student must be authorized to update the project commission funds.
        """
        response = self.student_misc_client.patch(
            "/projects/2/commission_funds/2", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cf_student_bad_request(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by any authenticated user.
        - The attributes to patch must be authorized.
        """
        response = self.student_misc_client.patch(
            "/projects/1/commission_funds/3",
            {"amount_earned": 1000},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cf_manager_bad_request(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by any authenticated user.
        - The attributes to patch must be authorized.
        """
        response = self.general_client.patch(
            "/projects/1/commission_funds/3",
            {"amount_asked": 1000},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_cf_serializer_error(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by any authenticated user.
        - The serializer fields must be correct.
        """
        patch_data = {"amount_asked": True}
        response = self.student_misc_client.patch(
            "/projects/1/commission_funds/3",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_cf_wrong_submission_date(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by any authenticated user.
        - The commission submission date must not be over.
        """
        commission_fund_id = 3
        commission = Commission.objects.get(id=1)
        commission.submission_date = "1968-05-03"
        commission.save()
        response = self.student_misc_client.patch(
            f"/projects/1/commission_funds/{commission_fund_id}",
            {"amount_asked": 1333},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_cf_success(self):
        """
        PATCH /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by any authenticated user.
        - ProjectCommissionFund object is correctly updated.
        - Project status is updated if validation is set, but only if all funds are validated.
        """
        patch_data = {"amount_asked": 1333}
        response = self.student_misc_client.patch(
            "/projects/1/commission_funds/3",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pcf_data = ProjectCommissionFund.objects.get(project_id=1, commission_fund_id=3)
        self.assertEqual(pcf_data.amount_asked, patch_data["amount_asked"])

        project = Project.objects.get(id=1)
        project.project_status = "PROJECT_PROCESSING"
        project.save()
        patch_data = {"is_validated_by_admin": True}
        response = self.general_client.patch(
            "/projects/1/commission_funds/3",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=1)
        self.assertEqual(project.project_status, "PROJECT_VALIDATED")

        project = Project.objects.get(id=2)
        project.project_status = "PROJECT_PROCESSING"
        project.save()
        patch_data = {"is_validated_by_admin": True}
        response = self.general_client.patch(
            "/projects/2/commission_funds/2",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=2)
        self.assertEqual(project.project_status, "PROJECT_PROCESSING")

        response = self.general_client.patch(
            "/projects/2/commission_funds/1",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=2)
        self.assertEqual(project.project_status, "PROJECT_VALIDATED")

    def test_delete_project_cf_anonymous(self):
        """
        DELETE /projects/{project_id}/commission_funds/{commission_fund_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/1/commission_funds/3")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_cf_not_found(self):
        """
        DELETE /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by a student client.
        - The ProjectCommissionFund object must exist.
        """
        response = self.student_misc_client.delete(
            "/projects/99999/commission_funds/99999"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_cf_forbidden(self):
        """
        DELETE /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by a student user.
        - The authenticated user must be authorized to update the project commission funds.
        """
        response = self.student_misc_client.delete("/projects/2/commission_funds/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_cf_success(self):
        """
        DELETE /projects/{project_id}/commission_funds/{commission_fund_id} .

        - The route can be accessed by a student user.
        - The authenticated user must be authorized to update the project commission funds.
        - ProjectCommissionFund object is correctly removed from db.
        """
        response = self.student_misc_client.delete("/projects/1/commission_funds/3")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        pcf_not_found = len(
            ProjectCommissionFund.objects.filter(project_id=1, commission_fund_id=3)
        )
        self.assertEqual(pcf_not_found, 0)
