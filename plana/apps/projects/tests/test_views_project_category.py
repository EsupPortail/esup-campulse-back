"""List of tests done on projects views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory


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

        """ Start a user member of an association that can submit projects. """
        self.student_site_user_id = 11
        self.student_site_user_name = "etudiant-asso-site@mail.tld"
        self.student_site_client = Client()
        data_student_site = {
            "username": self.student_site_user_name,
            "password": "motdepasse",
        }
        self.response = self.student_site_client.post(url_login, data_student_site)

        """ Start a user president of an association that can submit projects. """
        self.student_president_user_id = 13
        self.student_president_user_name = "president-asso-site@mail.tld"
        self.student_president_client = Client()
        data_student_president = {
            "username": self.student_president_user_name,
            "password": "motdepasse",
        }
        self.response = self.student_president_client.post(
            url_login, data_student_president
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

    def test_post_project_categories_forbidden_user(self):
        """
        POST /projects/categories .

        - The route can be accessed by any authenticated user.
        - The owner of the project must be the authenticated user.
        """
        post_data = {
            "project": 1,
            "category": 1,
        }
        response = self.student_offsite_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_categories_forbidden_association_user(self):
        """
        POST /projects/categories .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be a member of the association owning the project.
        """
        post_data = {
            "project": 2,
            "category": 1,
        }
        response = self.student_offsite_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_categories_forbidden_not_association_president(self):
        """
        POST /projects/categories .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be the president of the association owning the project.
        """
        post_data = {
            "project": 2,
            "category": 1,
        }
        response = self.student_site_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_categories_association_success(self):
        """
        POST /projects/categories .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be the president of the association owning the project.
        - The ProjectCategory link is created in db.
        - If the same ProjectCategory is attempted to be created, returns a HTTP 200 and is not created twice in db.
        """
        post_data = {
            "project": 2,
            "category": 3,
        }
        response = self.student_president_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            1,
            len(
                ProjectCategory.objects.filter(
                    project=post_data["project"], category=post_data["category"]
                )
            ),
        )

        response = self.student_president_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            1,
            len(
                ProjectCategory.objects.filter(
                    project=post_data["project"], category=post_data["category"]
                )
            ),
        )

    def test_delete_project_categories_anonymous(self):
        """
        DELETE /projects/{project_id}/category/{category_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/1/category/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_categories_not_found(self):
        """
        DELETE /projects/{project_id}/category/{category_id} .

        - The route can be accessed by any authenticated user.
        - The project must be existing.
        """
        project = 999
        category = 1
        response = self.general_client.delete(
            f"/projects/{project}/category/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_categories_forbidden_user(self):
        """
        DELETE /projects/{project_id}/category/{category_id} .

        - The route can be accessed by any authenticated user.
        - The owner of the project must be the authenticated user.
        """
        project = 1
        category = 1
        response = self.student_offsite_client.delete(
            f"/projects/{project}/category/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_categories_forbidden_association_user(self):
        """
        DELETE /projects/{project_id}/category/{category_id} .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be a member of the association owning the project.
        """
        project = 2
        category = 1
        response = self.student_offsite_client.delete(
            f"/projects/{project}/category/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_categories_forbidden_not_association_president(self):
        """
        DELETE /projects/{project_id}/category/{category_id} .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be the president of the association owning the project.
        """
        project = 2
        category = 1
        response = self.student_site_client.delete(
            f"/projects/{project}/category/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_categories_association_success(self):
        """
        DELETE /projects/{project_id}/category/{category_id} .

        - The route can be accessed by any authenticated user.
        - The authenticated user must be the president of the association owning the project.
        - The ProjectCategory link is deleted from db.
        - If the same ProjectCategory is attempted to be deleted, returns a HTTP 200 and not throwing error.
        """
        project = 2
        category = 1
        response = self.student_president_client.delete(
            f"/projects/{project}/category/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            0,
            len(ProjectCategory.objects.filter(project=project, category=category)),
        )

        response = self.student_president_client.delete(
            f"/projects/{project}/category/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            0,
            len(ProjectCategory.objects.filter(project=project, category=category)),
        )
