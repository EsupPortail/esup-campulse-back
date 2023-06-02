"""List of tests done on commissions views."""
import datetime
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.views.commission import ProjectCommissionFund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import GroupInstitutionFundUser


class CommissionDatesViewsTests(TestCase):
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
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "projects_projectcommissionfund.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on all tests."""
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

    def test_get_commissions_list(self):
        """
        GET /commissions/ .

        - There's at least one commission in the commissions list.
        - The route can be accessed by anyone.
        - We get the same amount of commissions through the model and through the view.
        - commission_dates filters by commission_date field.
        - is_site filters by is_site field.
        - only_next returns only one date by fund.
        - active_projects returns commissions depending on their projects statuses.
        - managed_commissions returns funds managed by current user.
        - managed_projects returns funds where current user manages projects.
        """
        commissions_cnt = Commission.objects.count()
        self.assertTrue(commissions_cnt > 0)

        response = self.client.get("/commissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

        commission_dates = ["2099-10-20", "2099-10-21"]
        commission_dates = [
            datetime.datetime.strptime(commission_date, "%Y-%m-%d").date()
            for commission_date in commission_dates
            if commission_date != ""
            and isinstance(
                datetime.datetime.strptime(commission_date, "%Y-%m-%d").date(),
                datetime.date,
            )
        ]
        response = self.client.get(
            f"/commissions/?commission_dates={','.join(str(x) for x in commission_dates)}"
        )
        commissions_cnt = Commission.objects.filter(
            commission_date__in=commission_dates
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

        response = self.client.get("/commissions/?is_site=true")
        commissions_cnt = Commission.objects.filter(
            id__in=Fund.objects.filter(is_site=True).values_list("id")
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

        response = self.client.get("/commissions/?only_next=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), Fund.objects.count())

        inactive_projects = Project.visible_objects.filter(
            project_status__in=Project.ProjectStatus.get_archived_project_statuses()
        )
        commissions_with_inactive_projects = Commission.objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                project_id__in=inactive_projects
            ).values_list("commission_date_id")
        )
        response = self.client.get("/commissions/?active_projects=false")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_with_inactive_projects.count())

        commissions_with_active_projects = Commission.objects.exclude(
            id__in=ProjectCommissionFund.objects.filter(
                project_id__in=inactive_projects
            ).values_list("commission_date_id")
        )
        response = self.client.get("/commissions/?active_projects=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_with_active_projects.count())

        managed_commissions = Commission.objects.filter(
            commission_id__in=Fund.objects.filter(
                institution_id__in=Institution.objects.filter(
                    id__in=GroupInstitutionFundUser.objects.filter(
                        user_id=self.manager_institution_user_id
                    ).values_list("institution_id")
                ).values_list("id")
            ).values_list("id")
        )
        response = self.institution_client.get("/commissions/?managed_commissions=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), managed_commissions.count())
        unmanaged_commissions = Commission.objects.exclude(
            commission_id__in=Fund.objects.filter(
                institution_id__in=Institution.objects.filter(
                    id__in=GroupInstitutionFundUser.objects.filter(
                        user_id=self.manager_institution_user_id
                    ).values_list("institution_id")
                ).values_list("id")
            ).values_list("id")
        )
        response = self.institution_client.get(
            "/commissions/?managed_commissions=false"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), unmanaged_commissions.count())

        commissions_with_managed_projects = Commission.objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                project_id__in=Project.visible_objects.filter(
                    association_id__in=Association.objects.filter(
                        institution_id__in=Institution.objects.filter(
                            id__in=GroupInstitutionFundUser.objects.filter(
                                user_id=self.manager_institution_user_id
                            ).values_list("institution_id")
                        ).values_list("id")
                    ).values_list("id")
                ).values_list("id")
            ).values_list("commission_date_id")
        )
        response = self.institution_client.get("/commissions/?managed_projects=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_with_managed_projects.count())

        commissions_not_with_managed_projects = Commission.objects.exclude(
            id__in=ProjectCommissionFund.objects.filter(
                project_id__in=Project.visible_objects.filter(
                    association_id__in=Association.objects.filter(
                        institution_id__in=Institution.objects.filter(
                            id__in=GroupInstitutionFundUser.objects.filter(
                                user_id=self.manager_institution_user_id
                            ).values_list("institution_id")
                        ).values_list("id")
                    ).values_list("id")
                ).values_list("id")
            ).values_list("commission_date_id")
        )
        response = self.institution_client.get("/commissions/?managed_projects=false")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_not_with_managed_projects.count())

    def test_post_commissions_anonymous(self):
        """
        POST /commissions/ .

        - An anonymous user can't execute this request.
        """
        post_data = {"submission_date": "2099-11-30", "commission_date": "2099-12-25"}
        response = self.client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_commissions_forbidden(self):
        """
        POST /commissions/ .

        - A user without proper permissions can't execute this request.
        """
        post_data = {
            "submission_date": "2099-11-30",
            "commission_date": "2099-12-25",
            "commission": 1,
        }
        response = self.student_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_commissions_wrong_dates(self):
        """
        POST /commissions/ .

        - submission_date cannot come after commission_date.
        """
        post_data = {
            "submission_date": "2099-12-25",
            "commission_date": "2099-11-30",
            "commission": 1,
        }
        response = self.general_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_commissions_too_old(self):
        """
        POST /commissions/ .

        - A commission taking place before today cannot be created.
        """
        post_data = {
            "submission_date": "1993-11-30",
            "commission_date": "1993-12-25",
            "commission": 1,
        }
        response = self.general_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_commissions_success(self):
        """
        POST /commissions/ .

        - A user with proper permissions can execute this request.
        """
        post_data = {
            "submission_date": "2099-11-30",
            "commission_date": "2099-12-25",
            "commission": 1,
        }
        response = self.general_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_commission_by_id_404(self):
        """
        GET /commissions/{id} .

        - An anonymous user can execute this request.
        """
        response = self.client.get("/commissions/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_commission_by_id_anonymous(self):
        """
        GET /commissions/{id} .

        - An anonymous user can execute this request.
        """
        response = self.client.get("/commissions/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_commission_by_id_405(self):
        """
        PUT /commissions/{id} .

        - The route returns a 405 everytime.
        """
        data = {"submission_date": "2099-11-30", "commission_date": "2099-12-25"}
        response = self.client.put("/commissions/1", data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_commission_anonymous(self):
        """
        PATCH /commissions/{id} .

        - An anonymous user can't execute this request.
        """
        patch_data = {"submission_date": "2099-11-30", "commission_date": "2099-12-25"}
        response = self.client.patch(
            "/commissions/1",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_commission_404(self):
        """
        PATCH /commissions/{id} .

        - A user with proper permissions can execute this request.
        - Commission must exist.
        """
        patch_data = {"submission_date": "2099-11-30", "commission_date": "2099-12-25"}
        response = self.general_client.patch(
            "/commissions/999",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_commission_forbidden(self):
        """
        PATCH /commissions/{id} .

        - A user without proper permissions can't execute this request.
        """
        patch_data = {"submission_date": "2099-11-30", "commission_date": "2099-12-25"}
        response = self.student_client.patch(
            "/commissions/1",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_commission_wrong_dates(self):
        """
        PATCH /commissions/{id} .

        - submission_date cannot come after commission_date.
        """
        patch_data = {"submission_date": "2099-12-25", "commission_date": "2099-11-30"}
        response = self.general_client.patch(
            "/commissions/1",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_commission_too_old(self):
        """
        PATCH /commissions/{id} .

        - A commission date cannot be updated to a date taking place before today.
        """
        patch_data = {"submission_date": "1993-11-30", "commission_date": "2099-12-25"}
        response = self.general_client.patch(
            "/commissions/1",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_commission_success(self):
        """
        PATCH /commissions/{id} .

        - A user with proper permissions can execute this request.
        """
        patch_data = {"submission_date": "2099-11-30", "commission_date": "2099-12-25"}
        response = self.general_client.patch(
            "/commissions/1",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        commission_date = Commission.objects.get(id=1)
        self.assertEqual(
            patch_data["submission_date"],
            commission_date.submission_date.strftime("%Y-%m-%d"),
        )

    def test_delete_commission_anonymous(self):
        """
        DELETE /commissions/{id} .

        - An anonymous user can't execute this request.
        """
        response = self.client.delete("/commissions/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_commission_404(self):
        """
        DELETE /commissions/{id} .

        - A user with proper permissions can execute this request.
        - Commission must exist.
        """
        response = self.general_client.delete("/commissions/999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_commission_forbidden(self):
        """
        DELETE /commissions/{id} .

        - A user without proper permissions can't execute this request.
        """
        response = self.student_client.delete("/commissions/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_commission_too_old(self):
        """
        DELETE /commissions{id} .

        - A commission taking place before today cannot be deleted.
        """
        commission_date_id = 1
        commission_date = Commission.objects.get(id=commission_date_id)
        commission_date.commission_date = "1993-12-25"
        commission_date.save()
        response = self.general_client.delete(f"/commissions/{commission_date_id}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_commission_non_draft_projects(self):
        """
        DELETE /commissions/{id} .

        - A commission with non-draft projects linked cannot be deleted.
        """
        response = self.general_client.delete("/commissions/3")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_commission_success(self):
        """
        DELETE /commissions/{id} .

        - A user with proper permissions can execute this request.
        - Commission object is correctly deleted
        """
        response = self.general_client.delete("/commissions/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        commission_date = Commission.objects.filter(id=1)
        self.assertEqual(len(commission_date), 0)
