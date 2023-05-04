"""List of tests done on projects comments links views"""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.models.project import Project


class ProjectCommentLinksViewsTests(TestCase):

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
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start clients used on tests"""
        cls.client = Client()
        url_login = reverse("rest_login")

        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.general_client = Client()
        data_general = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse"
        }
        cls.response = cls.general_client.post(url_login, data_general)

        cls.student_president_user_id = 13
        cls.student_president_user_name = "president-asso-site@mail.tld"
        cls.student_president_client = Client()
        data_student_president = {
            "username": cls.student_president_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_president_client.post(
            url_login, data_student_president
        )

    def test_get_project_comments_student(self):
        """
        GET /projects/categories .

        - A student user gets comments where projects rights are OK.
        """
        response = self.student_president_client.get("/projects/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)