"""List of tests done on commission exports views."""
import csv
import io

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.commissions.views.commission import ProjectCommissionFund
from plana.apps.projects.models.project import Project


class CommissionExportsViewsTests(TestCase):
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
        "projects_project.json",
        "projects_projectcommissionfund.json",
        "users_associationuser.json",
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

    def test_commission_projects_csv_export_anonymous(self):
        """
        GET /commissions/{id}/csv_export .

        - An anonymous user can't execute this request.
        """
        response = self.client.get("/commissions/1/csv_export")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_commission_projects_csv_export_success_general_manager(self):
        """
        GET /commissions/{id}/csv_export .

        - The route can be accessed by a manager user.
        - All projects linked to the selected commission from db are returned in the CSV.
        """
        commission_id = 1
        response = self.general_client.get(f"/commissions/{commission_id}/csv_export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))

        total = Project.objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                ).values("id")
            )
        ).count()
        # -1 because of CSV header
        self.assertEqual(len(list(csv_reader)) - 1, total)
