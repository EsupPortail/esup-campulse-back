"""List of tests done on commissions views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.views.commission_date import ProjectCommissionDate
from plana.apps.institutions.models import Institution
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import GroupInstitutionCommissionUser


class CommissionsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "projects_projectcommissiondate.json",
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on all tests."""
        cls.client = Client()
        url_login = reverse("rest_login")

        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

    def test_get_commissions_list(self):
        """
        GET /commissions/ .

        - There's at least one commission in the commissions list.
        - The route can be accessed by anyone.
        - We get the same amount of commissions through the model and through the view.
        - Commissions details are returned (test the "name" attribute).
        - Filter by acronym is available.
        """
        commissions_cnt = Commission.objects.count()
        self.assertTrue(commissions_cnt > 0)

        response = self.client.get("/commissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

        commission_1 = content[0]
        self.assertTrue(commission_1.get("name"))

        acronym = "FSDIE"
        response = self.client.get(f"/commissions/?acronym={acronym}")
        self.assertEqual(response.data[0]["acronym"], acronym)

        response = self.client.get("/commissions/?only_next=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

    def test_get_commissions_dates_list(self):
        """
        GET /commissions/commission_dates .

        - There's at least one commission date in the commission dates list.
        - The route can be accessed by anyone.
        - We get the same amount of commission dates through the model and through the view.
        - only_next returns only one date by commission.
        - active_projects returns commissions dates depending on their projects statuses.
        - managed_projects returns commissions where current user manages projects.
        """
        commission_dates_cnt = CommissionDate.objects.count()
        self.assertTrue(commission_dates_cnt > 0)

        response = self.client.get("/commissions/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commission_dates_cnt)

        response = self.client.get("/commissions/commission_dates?only_next=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), Commission.objects.count())

        inactive_projects = Project.objects.filter(
            project_status__in=Project.ProjectStatus.get_archived_project_statuses()
        )
        commission_dates_with_inactive_projects = CommissionDate.objects.filter(
            id__in=ProjectCommissionDate.objects.filter(
                project_id__in=inactive_projects
            ).values_list("commission_date_id")
        )
        response = self.client.get(
            "/commissions/commission_dates?active_projects=false"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commission_dates_with_inactive_projects.count())
        commission_dates_with_active_projects = CommissionDate.objects.exclude(
            id__in=ProjectCommissionDate.objects.filter(
                project_id__in=inactive_projects
            ).values_list("commission_date_id")
        )
        response = self.client.get("/commissions/commission_dates?active_projects=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commission_dates_with_active_projects.count())

        commission_dates_with_managed_projects = CommissionDate.objects.filter(
            id__in=ProjectCommissionDate.objects.filter(
                project_id__in=Project.objects.filter(
                    association_id__in=Association.objects.filter(
                        institution_id__in=Institution.objects.filter(
                            id__in=GroupInstitutionCommissionUser.objects.filter(
                                user_id=self.manager_institution_user_id
                            ).values_list("institution_id")
                        ).values_list("id")
                    ).values_list("id")
                ).values_list("id")
            ).values_list("commission_date_id")
        )
        response = self.institution_client.get(
            "/commissions/commission_dates?managed_projects=true"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commission_dates_with_managed_projects.count())
        commission_dates_not_with_managed_projects = CommissionDate.objects.exclude(
            id__in=ProjectCommissionDate.objects.filter(
                project_id__in=Project.objects.filter(
                    association_id__in=Association.objects.filter(
                        institution_id__in=Institution.objects.filter(
                            id__in=GroupInstitutionCommissionUser.objects.filter(
                                user_id=self.manager_institution_user_id
                            ).values_list("institution_id")
                        ).values_list("id")
                    ).values_list("id")
                ).values_list("id")
            ).values_list("commission_date_id")
        )
        response = self.institution_client.get(
            "/commissions/commission_dates?managed_projects=false"
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(
            len(content), commission_dates_not_with_managed_projects.count()
        )
