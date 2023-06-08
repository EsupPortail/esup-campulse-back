"""List of tests done on commission funds views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.commissions.models import CommissionFund


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
        "commissions_commissionfund.json",
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

        cls.student_user_id = 9
        cls.student_user_name = "etudiant-porteur@mail.tld"
        cls.student_client = Client()
        data_student = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_client.post(url_login, data_student)

    def test_get_commission_funds_list(self):
        """
        GET /commissions/commission_funds/ .
        - There's at least one commission_fund in the list.
        - The route can be accessed by anyone.
        - We get the same amount of commission_funds through the model and through the view.
        """
        cf_count = CommissionFund.objects.count()
        self.assertTrue(cf_count > 0)

        response = self.client.get("/commissions/commission_funds/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), cf_count)

    def test_post_commission_fund_anonymous(self):
        """
        POST /commissions/commission_funds/ .

        - An anonymous user can't execute this request.
        """
        post_data = {"commission": 3, "fund": 2}
        response = self.client.post("/commissions/commission_funds/", post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_commission_fund_forbidden(self):
        """
        POST /commissions/commission_funds/ .

        - A user without proper permissions cannot execute this request.
        """
        post_data = {"commission": 3, "fund": 2}
        response = self.student_client.post("/commissions/commission_funds/", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_commission_fund_already_exists(self):
        """
        POST /commissions/commission_funds/ .

        - A commission and a fund cannot be linked twice together.
        """
        post_data = {"commission": 1, "fund": 1}
        response = self.general_client.post("/commissions/commission_funds/", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_commission_fund_success(self):
        """
        POST /commissions/commission_funds/ .

        - A user with proper permissions can execute this request.
        """
        # TODO : complete this test
        post_data = {"commission": 3, "fund": 2}
        response = self.general_client.post("/commissions/commission_funds/", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
