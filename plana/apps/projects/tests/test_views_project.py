"""List of tests done on projects views."""
import json

from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import AssociationUser


class ProjectsViewsTests(TestCase):
    """Main tests class."""

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

        """ Start a user misc that can submit personal projects. """
        self.student_misc_user_id = 9
        self.student_misc_user_name = "etudiant-porteur@mail.tld"
        self.student_misc_client = Client()
        data_student_misc = {
            "username": self.student_misc_user_name,
            "password": "motdepasse",
        }
        self.response = self.student_misc_client.post(url_login, data_student_misc)

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

    def test_get_project_anonymous(self):
        """
        GET /projects/ .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_student(self):
        """
        GET /projects/ .

        - A student user gets projects where rights are OK.
        """
        response = self.student_misc_client.get("/projects/")
        user_associations_ids = AssociationUser.objects.filter(
            user_id=self.student_misc_user_id
        ).values_list("association_id")
        user_projects_cnt = Project.objects.filter(
            models.Q(user_id=self.student_misc_user_id)
            | models.Q(association_id__in=user_associations_ids)
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), user_projects_cnt)

    def test_get_project_manager(self):
        """
        GET /projects/ .

        - A general manager user gets all projects.
        """
        response = self.general_client.get("/projects/")
        projects_cnt = Project.objects.all().count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_cnt)

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

        - The route can be accessed by a student user.
        - Project must have at least one affectation (user or association).
        - If linked to an association, the association must already exist.
        - Project cannot have multiple affectations.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "location": "address",
        }
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project_data["association"] = 9999
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        project_data["association"] = 2
        project_data["user"] = self.student_president_user_id
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_forbidden_user(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - User must have 'can_submit_projects' attribute set to True to sumbit a project.
        - User in the request must be the authenticated user.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "location": "address",
            "user": 10,
        }
        response = self.student_offsite_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        project_data["user"] = 999
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_forbidden_association(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - Association must have 'can_submit_associations' attribute set to True to submit projects.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "location": "address",
            "association": 3,
        }
        response = self.student_offsite_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_forbidden_association_role(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - The authenticated user must be a member of the association to create projects related to it.
        - User must be president or delegated president of its association to submit projects.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "location": "address",
            "association": 1,
        }
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        project_data["association"] = 2
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_association_success(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - To create a project for an association, the authenticated user must be president.
        - Project is created in database.
        """
        project_data = {
            "name": "Testing creation association",
            "goals": "Goals",
            "location": "address",
            "association": 2,
        }
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = Project.objects.filter(name="Testing creation association")
        self.assertEqual(len(results), 1)

    def test_post_project_user_success(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - The user in the request must be the authenticated user.
        - Project is created in database.
        """
        project_data = {
            "name": "Testing creation user",
            "goals": "Goals",
            "location": "address",
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = Project.objects.filter(name="Testing creation user")
        self.assertEqual(len(results), 1)

    def test_get_project_by_id_anonymous(self):
        """
        GET /projects/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_by_id_forbidden_student(self):
        """
        GET /projects/{id} .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.get("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_by_id(self):
        """
        GET /projects/{id} .

        - The route can be accessed by a manager user.
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

    def test_put_project(self):
        """
        PUT /projects/{id} .

        - Always returns a 405.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.general_client.put(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_anonymous(self):
        """
        PATCH /projects/{id} .

        - An anonymous user cannot execute this request.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.client.patch(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_forbidden_student(self):
        """
        PATCH /projects/{id} .

        - An student user not owning the project cannot execute this request.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.student_offsite_client.patch(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_not_found(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Project must be existing.
        """
        patch_data = {"goals": "Testing patching"}
        response = self.student_misc_client.patch(
            "/projects/999", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_wrong_status(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Status must be in authorized status list.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.student_misc_client.patch(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_forbidden_user(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - The project owner must be the authenticated user.
        """
        patch_data = {"description": "new desc"}
        response = self.student_site_client.patch(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_user_success(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - The project is correctly updated in db.
        """
        patch_data = {"summary": "new summary"}
        response = self.student_misc_client.patch(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=1)
        self.assertEqual(project.summary, "new summary")

    def test_patch_project_manager_error(self):
        """
        PATCH /projects/{id} .

        - The route cannot be accessed by a manager user.
        """
        patch_data = {"description": "new desc"}
        response = self.general_client.patch(
            "/projects/1", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_project_restricted(self):
        """
        PUT /projects/{id}/restricted .

        - Always returns a 405.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.general_client.put(
            "/projects/1/restricted", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_restricted_anonymous(self):
        """
        PATCH /projects/{id}/restricted .

        - An anonymous user cannot execute this request.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.client.patch(
            "/projects/1/restricted", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_restricted_forbidden_student(self):
        """
        PATCH /projects/{id}/restricted .

        - An student user cannot execute this request.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.student_offsite_client.patch(
            "/projects/1/restricted", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_restricted_not_found(self):
        """
        PATCH /projects/{id}/restricted .

        - The route can be accessed by a manager user.
        - Project must be existing.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.general_client.patch(
            "/projects/999/restricted", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_restricted_manager(self):
        """
        PATCH /projects/{id}/restricted .

        - The route can be accessed by a manager user.
        - Project must exist.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.general_client.patch(
            "/projects/1/restricted", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=1)
        self.assertEqual(project.project_status, "PROJECT_REJECTED")
