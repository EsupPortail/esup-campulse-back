"""List of tests done on commissions views."""

import datetime
import json

from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.views.commission import ProjectCommissionFund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import GroupInstitutionFundUser


class CommissionDatesViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "tests/account_emailaddress.json",
        "associations_activityfield.json",
        "tests/associations_association.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/contents_setting.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "tests/projects_project.json",
        "tests/projects_projectcommissionfund.json",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
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
        """
        commissions_cnt = Commission.objects.count()

        response = self.client.get("/commissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

    def test_get_commissions_list_filter_is_site(self):
        """
        GET /commissions/ .

        - is_site filters by is_site field.
        """
        response = self.client.get("/commissions/?is_site=true")
        commissions_cnt = Commission.objects.filter(
            id__in=CommissionFund.objects.filter(
                fund__in=Fund.objects.filter(is_site=True)
            ).values_list("commission_id")
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

    def test_get_commissions_list_filter_funds(self):
        """
        GET /commissions/ .

        - funds filters by Fund linked to Commission through CommissionFund.
        """
        fund_ids = [1, 3]
        response = self.client.get(f"/commissions/?funds={','.join(str(x) for x in fund_ids)}")
        commissions_cnt = Commission.objects.filter(
            id__in=CommissionFund.objects.filter(fund_id__in=fund_ids).values_list("commission_id")
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

    def test_get_commissions_list_filter_open_to_projects(self):
        """
        GET /commissions/ .

        - is_open_to_projects returns only one date by fund.
        """
        response_true = self.client.get("/commissions/?is_open_to_projects=true")
        commissions_cnt = Commission.objects.filter(is_open_to_projects=True).count()
        content = json.loads(response_true.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

        response_false = self.client.get("/commissions/?is_open_to_projects=false")
        commissions_cnt = Commission.objects.filter(is_open_to_projects=False).count()
        content = json.loads(response_false.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

    # FIXME : more precise unittest
    def test_get_commissions_list_filter_active_projects(self):
        """
        GET /commissions/ .

        - with_active_projects returns commissions depending on their projects statuses.
        - only_with_active_projects returns commissions depending on their projects statuses.
        """
        # Empty commissions
        commissions_ids_without_projects = Commission.objects.filter(
            commissionfund__projectcommissionfund__project__isnull=True
        ).values_list("id", flat=True).distinct()

        # Inactive projects related commissions
        archived_visible_projects = Project.visible_objects.filter(
            project_status__in=Project.ProjectStatus.get_archived_project_statuses()
        )
        commissions_ids_with_inactive_projects = Commission.objects.filter(
            commissionfund__projectcommissionfund__project__in=archived_visible_projects
        ).values_list("id", flat=True).distinct()

        # Active projects related commissions
        active_visible_projects = Project.visible_objects.exclude(
            project_status__in=Project.ProjectStatus.get_archived_project_statuses()
        )
        commissions_ids_with_active_projects = Commission.objects.filter(
            commissionfund__projectcommissionfund__project__in=active_visible_projects
        ).values_list("id", flat=True).distinct()

        commissions_with_inactive_projects = Commission.objects.filter(
            models.Q(id__in=commissions_ids_with_inactive_projects) | models.Q(id__in=commissions_ids_without_projects)
        )
        response_wapf = self.client.get("/commissions/?with_active_projects=false")
        content_wapf = json.loads(response_wapf.content.decode("utf-8"))
        self.assertEqual(len(content_wapf), commissions_with_inactive_projects.count())

        commissions_with_active_projects = Commission.objects.filter(
            models.Q(id__in=commissions_ids_with_active_projects) | models.Q(id__in=commissions_ids_without_projects)
        )
        response_wapt = self.client.get("/commissions/?with_active_projects=true")
        content_wapt = json.loads(response_wapt.content.decode("utf-8"))
        self.assertEqual(len(content_wapt), commissions_with_active_projects.count())

        commissions_only_with_inactive_projects = Commission.objects.filter(
            id__in=commissions_ids_with_inactive_projects
        ).exclude(id__in=commissions_ids_with_active_projects)
        response_owapf = self.client.get("/commissions/?only_with_active_projects=false")
        content_owapf = json.loads(response_owapf.content.decode("utf-8"))
        self.assertEqual(len(content_owapf), commissions_only_with_inactive_projects.count())

        commissions_only_with_active_projects = Commission.objects.exclude(
            id__in=commissions_ids_with_inactive_projects
        ).filter(id__in=commissions_ids_with_active_projects)
        response_owapt = self.client.get("/commissions/?only_with_active_projects=true")
        content_owapt = json.loads(response_owapt.content.decode("utf-8"))
        self.assertEqual(len(content_owapt), commissions_only_with_active_projects.count())

    def test_get_commissions_list_filter_managed_projects(self):
        """
        GET /commissions/ .

        - managed_projects returns funds where current user manages projects.
        """
        user_id = self.manager_institution_user_id
        commissions_with_managed_projects = Commission.objects.filter(
            models.Q(
                commissionfund__projectcommissionfund__project__in=Project.visible_objects.all(),
                commissionfund__projectcommissionfund__project__association__institution__groupinstitutionfunduser__user_id=user_id
            )
            | models.Q(commissionfund__fund__institution__groupinstitutionfunduser__user_id=user_id)
        )
        response = self.institution_client.get("/commissions/?managed_projects=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_with_managed_projects.count())

        commissions_not_with_managed_projects = Commission.objects.exclude(
            id__in=commissions_with_managed_projects.values_list("id", flat=True)
        )
        response = self.institution_client.get("/commissions/?managed_projects=false")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_not_with_managed_projects.count())

    def test_post_commissions_anonymous(self):
        """
        POST /commissions/ .

        - An anonymous user can't execute this request.
        """
        post_data = {
            "submission_date": "2099-11-30",
            "commission_date": "2099-12-25",
            "name": "New Commission",
        }
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
            "name": "New Commission",
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
            "name": "New Commission",
        }
        response = self.general_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("inconsistent_dates", response.data)

    def test_post_commissions_too_old(self):
        """
        POST /commissions/ .

        - A commission taking place before today cannot be created.
        """
        post_data = {
            "submission_date": "1993-11-30",
            "commission_date": "1993-12-25",
            "name": "New Commission",
        }
        response = self.general_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("submission_date", response.data)

    def test_post_commissions_name_already_taken(self):
        """
        POST /commissions/ .

        - The commission name must be unique, aven unaccented and without spaces.
        """
        post_data = {
            "submission_date": "2099-11-23",
            "commission_date": "2099-12-25",
            "name": "Commissionnumero 1",
        }
        response = self.general_client.post("/commissions/", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_post_commissions_success(self):
        """
        POST /commissions/ .

        - A user with proper permissions can execute this request.
        """
        post_data = {
            "submission_date": "2099-11-30",
            "commission_date": "2099-12-25",
            "name": "New Commission",
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

    def test_patch_commission_wrong_name(self):
        """
        PATCH /commissions/{id} .

        - The commission name must be unique, aven unaccented and without spaces.
        """
        patch_data = {"name": "Commissionnumero1"}
        response = self.general_client.patch(
            "/commissions/2",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("similar_name", response.data)

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
        self.assertIn("inconsistent_dates", response.data)

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
        self.assertIn("past_date", response.data)

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
        response = self.general_client.delete("/commissions/1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_commission_success(self):
        """
        DELETE /commissions/{id} .

        - A user with proper permissions can execute this request.
        - Commission object is correctly deleted
        """
        response = self.general_client.delete("/commissions/3")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        commission_date = Commission.objects.filter(id=3)
        self.assertEqual(len(commission_date), 0)
