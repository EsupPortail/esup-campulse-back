"""List of tests done on projects views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.projects.models.project import Project


class ProjectsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissiondate.json",
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "associations_association.json",
        "users_associationusers.json",
        "associations_activityfield.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "users_user.json",
        "account_emailaddress.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "users_groupinstitutioncommissionusers.json",
    ]

    def setUp(self):
        """Start a default anonymous client."""
        self.client = Client()
        url_login = reverse("rest_login")

        """ Start a manager general client used on a majority of tests. """
        self.manager_general_user_id = 3
        self.manager_general_user_name = "gestionnaire-svu@mail.tld"
        self.general_client = Client()
        data_general = {
            "username": self.manager_general_user_name,
            "password": "motdepasse",
        }
        self.response = self.general_client.post(url_login, data_general)

        """ Start a user member of an association that cannot submit personal or association projects. """
        self.student_offsite_user_id = 10
        self.student_offsite_user_name = "etudiant-asso-hors-site@mail.tld"
        self.student_offsite_client = Client()
        data_student_offsite = {
            "username": self.student_offsite_user_name,
            "password": "motdepasse",
        }
        self.response = self.student_offsite_client.post(
            url_login, data_student_offsite
        )

    def test_post_project_categories_anonymous(self):
        """
        POST /projects/categories .

        - An anonymous user cannot execute this request.
        """
        response = self.client.post(
            "/projects/categories", {"name": "Testing anonymous"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_project_categories_not_found(self):
        """
        POST /projects/categories .

        - The route can be accessed by any authenticated user.
        - The project must be existing
        """
        post_data = {
            "project": 999,
            "category": 1,
        }
        response = self.general_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_forbidden_user(self):
        """
        POST /projects/ .

        - The route can be accessed by any authenticated user.
        - The owner of the project must be the authenticated user.
        """
        post_data = {
            "project": 1,
            "category": 1,
        }
        response = self.student_offsite_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
