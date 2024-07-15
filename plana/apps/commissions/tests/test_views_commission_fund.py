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
        GET /commissions/funds .

        - There's at least one commission_fund in the list.
        - The route can be accessed by anyone.
        - We get the same amount of commission_funds through the model and through the view.
        """
        cf_count = CommissionFund.objects.count()
        self.assertTrue(cf_count > 0)

        response = self.client.get("/commissions/funds")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), cf_count)

    def test_post_commission_fund_anonymous(self):
        """
        POST /commissions/funds .

        - An anonymous user can't execute this request.
        """
        post_data = {"commission": 3, "fund": 2}
        response = self.client.post("/commissions/funds", post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_commission_fund_not_found(self):
        """
        POST /commissions/funds .

        - Commission and fund must exist.
        """
        post_data = {"commission": 999, "fund": 2}
        response = self.general_client.post("/commissions/funds", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        post_data = {"commission": 2, "fund": 999}
        response = self.general_client.post("/commissions/funds", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_commission_fund_forbidden(self):
        """
        POST /commissions/funds .

        - A user without proper permissions cannot execute this request.
        """
        post_data = {"commission": 3, "fund": 2}
        response = self.student_client.post("/commissions/funds", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_commission_fund_already_exists(self):
        """
        POST /commissions/funds .

        - A commission and a fund cannot be linked together twice.
        """
        post_data = {"commission": 1, "fund": 1}
        response = self.general_client.post("/commissions/funds", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_commission_fund_success(self):
        """
        POST /commissions/funds .

        - A user with proper permissions can execute this request.
        """
        commission = 3
        fund = 2
        post_data = {"commission": commission, "fund": fund}
        response = self.general_client.post("/commissions/funds", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        commission_fund = CommissionFund.objects.filter(commission_id=commission, fund_id=fund)
        self.assertEqual(commission_fund.count(), 1)

    def test_get_commission_funds_by_id_404(self):
        """
        GET /commissions/{commission_id}/funds .

        - The route returns a 404 if a wrong commission id is given.
        """
        response = self.client.get("/commissions/99999/funds")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_commission_funds_by_id(self):
        """
        GET /commissions/{commission_id}/funds .

        - The route can be accessed by everyone.
        - Correct commission funds are returned.
        """
        commission_id = 1
        commission_test_cnt = CommissionFund.objects.filter(commission_id=commission_id).count()
        response = self.client.get(f"/commissions/{commission_id}/funds")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commission_test_cnt)

    def test_delete_commission_funds_anonymous(self):
        """
        DELETE /commissions/{commission_id}/funds/{fund_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/commissions/1/funds/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_commission_funds_not_found(self):
        """
        DELETE /commissions/{commission_id}/funds/{fund_id} .

        - The route can be accessed by a manager user.
        - Commission and fund must exist.
        """
        commission_id = 999
        fund_id = 1
        response = self.general_client.delete(f"/commissions/{commission_id}/funds/{fund_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        commission_id = 1
        fund_id = 999
        response = self.general_client.delete(f"/commissions/{commission_id}/funds/{fund_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_commission_funds_forbidden_user(self):
        """
        DELETE /commissions/{commission_id}/funds/{fund_id} .

        - A student user cannot execute this request.
        """
        commission_id = 1
        fund_id = 1
        response = self.student_client.delete(f"/commissions/{commission_id}/funds/{fund_id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_commission_funds_success(self):
        """
        DELETE /commissions/{commission_id}/funds/{fund_id} .

        - The route can be accessed by a manager user.
        - The ProjectCategory link is deleted from db.
        - If the same ProjectCategory is attempted to be deleted, returns a HTTP 404.
        """
        commission_id = 1
        fund_id = 1
        response = self.general_client.delete(f"/commissions/{commission_id}/funds/{fund_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            0,
            len(CommissionFund.objects.filter(commission_id=commission_id, fund_id=fund_id)),
        )

        response = self.general_client.delete(f"/commissions/{commission_id}/funds/{fund_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
