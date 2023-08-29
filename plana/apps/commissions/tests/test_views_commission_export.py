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

    def test_commission_projects_export_anonymous(self):
        """
        GET /commissions/{id}/export .

        - An anonymous user can't execute this request.
        """
        response = self.client.get("/commissions/1/export")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_commission_projects_export_unauthorized(self):
        """
        GET /commissions/{id}/export .

        - Commission must exist.
        """
        response = self.general_client.get("/commissions/9999/export")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_commission_projects_export_not_found(self):
        """
        GET /commissions/{id}/export .

        - A student only sees own projects.
        """
        commission_id = 1

        response = self.student_client.get(
            f"/commissions/{commission_id}/export?mode=pdf"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.student_client.get(f"/commissions/{commission_id}/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))

        total = Project.visible_objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                ).values("id")
            )
        ).count()
        # -1 because of CSV header
        self.assertNotEqual(len(list(csv_reader)) - 1, total)

    def test_commission_projects_export_success_general_manager(self):
        """
        GET /commissions/{id}/export .

        - The route can be accessed by a manager user.
        - Manager can only see linked fund commissions.
        - All projects linked to the selected commission from db are returned in the CSV.
        - project_ids argument filters by Project IDs.
        """
        commission_id = 1

        response = self.institution_client.get(f"/commissions/{commission_id}/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))

        total = Project.visible_objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                ).values("id")
            )
        ).count()
        # -1 because of CSV header
        self.assertNotEqual(len(list(csv_reader)) - 1, total)

        response = self.general_client.get(
            f"/commissions/{commission_id}/export?project_ids=4,10"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))

        total = Project.visible_objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                ).values("id")
            )
        )
        total = total.filter(id__in=[4, 10]).count()
        # -1 because of CSV header
        self.assertEqual(len(list(csv_reader)) - 1, total)
