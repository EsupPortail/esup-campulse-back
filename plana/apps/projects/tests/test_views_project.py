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

    def test_post_project_anonymous(self):
        """
        POST /projects/ .

        - An anonymous user cannot execute this request.
        """
        response = self.client.post("/projects/", {"name": "Testing anonymous"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_project_bad_request(self):
        """
        POST /projects/ .

        - The route can be accessed by any authenticated user.
        - Project must have at least one affectation (user or association).
        - If linked to an association, the association must already exist.
        - Project cannot have multiple affectations.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "location": "address",
        }
        response = self.general_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project_data["association"] = 9999
        response = self.general_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project_data["user"] = 2
        response = self.general_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #    def test_post_project(self):
    #        """
    #        POST /projects/ .
    #
    #        - The route can be accessed by any authenticated user with correct permissions.
    #        - Project is created in database.
    #        """
    #        project_data = {
    #            "name": "Testing creation",
    #            "goals": "Goals",
    #            "location": "address",
    #        }
    #        response = self.general_client.post("/projects/", project_data)
    #        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #        results = Project.objects.filter(name="Testing creation")
    #        self.assertEqual(len(results), 1)

    def test_get_project_by_id_anonymous(self):
        """
        GET /projects/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_by_id(self):
        """
        GET /projects/{id} .

        - The route can be accessed by any authenticated user.
        - Correct projects details are returned (test the "name" attribute).
        """
        project_id = 1
        project_test = Project.objects.get(id=project_id)
        response = self.general_client.get(f"/projects/{project_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["name"], project_test.name)

    def test_get_project_by_id_404(self):
        """
        GET /projects/{id} .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
