"""List of tests done on projects categories links views."""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.users.models.user import GroupInstitutionFundUser


class ProjectCategoryLinksViewsTests(TestCase):
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
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start clients used on tests."""
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

        cls.student_offsite_user_id = 10
        cls.student_offsite_user_name = "etudiant-asso-hors-site@mail.tld"
        cls.student_offsite_client = Client()
        data_student_offsite = {
            "username": cls.student_offsite_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_offsite_client.post(url_login, data_student_offsite)

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

    def test_get_project_categories_anonymous(self):
        """
        GET /projects/categories .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/categories")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_categories_student(self):
        """
        GET /projects/categories .

        - A student user gets categories where projects rights are OK.
        """
        response = self.student_offsite_client.get("/projects/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_categories_institution_manager(self):
        """
        GET /projects/categories .

        - An institution manager user gets project categories for correct projects.
        """
        response = self.institution_client.get("/projects/categories")
        user_institutions_ids = Institution.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(
                user_id=self.manager_institution_user_id
            ).values_list("institution_id")
        )
        projects_categories_cnt = ProjectCategory.objects.filter(
            project_id__in=Project.visible_objects.filter(
                association_id__in=Association.objects.filter(
                    institution_id__in=user_institutions_ids
                ).values_list("id")
            )
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_categories_cnt)

    def test_get_project_categories_manager(self):
        """
        GET /projects/categories .

        - A general manager user gets all project categories.
        - project_id argument filters by Project ID.
        """
        response = self.general_client.get("/projects/categories")
        projects_categories_cnt = ProjectCategory.objects.all().count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_categories_cnt)

        response = self.general_client.get("/projects/categories?project_id=2")
        projects_categories_cnt = ProjectCategory.objects.filter(project_id=2).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_categories_cnt)

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

        - The route can be accessed by a student user.
        - The project must exist.
        """
        post_data = {
            "project": 999,
            "category": 1,
        }
        response = self.student_offsite_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_categories_forbidden_user(self):
        """
        POST /projects/categories .

        - The route can be accessed by a student user.
        - The owner of the project must be the authenticated user.
        """
        post_data = {
            "project": 1,
            "category": 1,
        }
        response = self.student_offsite_client.post("/projects/categories", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_categories_association_success(self):
        """
        POST /projects/categories .

        - The route can be accessed by a student user.
        - The authenticated user must be the president of the association owning the project.
        - The ProjectCategory link is created in db.
        - Project edition date is updated.
        - If the same ProjectCategory is attempted to be created, returns a HTTP 200 and is not created twice in db.
        """
        post_data = {
            "project": 2,
            "category": 3,
        }
        old_project_edition_date = Project.visible_objects.get(
            id=post_data["project"]
        ).edition_date
        response = self.student_president_client.post("/projects/categories", post_data)
        new_project_edition_date = Project.visible_objects.get(
            id=post_data["project"]
        ).edition_date
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            1,
            len(
                ProjectCategory.objects.filter(
                    project=post_data["project"], category=post_data["category"]
                )
            ),
        )
        self.assertNotEqual(old_project_edition_date, new_project_edition_date)

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

    def test_get_project_categories_by_id_anonymous(self):
        """
        GET /projects/{project_id}/categories .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1/categories")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_categories_by_id_404(self):
        """
        GET /projects/{project_id}/categories .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/categories")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_categories_by_id_forbidden_student(self):
        """
        GET /projects/{project_id}/categories .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.get("/projects/1/categories")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_categories_by_id(self):
        """
        GET /projects/{project_id}/categories .

        - The route can be accessed by a manager user.
        - The route can be accessed by a student user.
        - Correct projects categories are returned.
        """
        project_id = 1
        project_test_cnt = ProjectCategory.objects.filter(project_id=project_id).count()
        response = self.general_client.get(f"/projects/{project_id}/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

        project_id = 2
        project_test_cnt = ProjectCategory.objects.filter(project_id=project_id).count()
        response = self.student_president_client.get(
            f"/projects/{project_id}/categories"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

    def test_delete_project_categories_anonymous(self):
        """
        DELETE /projects/{project_id}/categories/{category_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/1/categories/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_categories_not_found(self):
        """
        DELETE /projects/{project_id}/categories/{category_id} .

        - The route can be accessed by a student user.
        - The project must exist.
        """
        project = 999
        category = 1
        response = self.student_offsite_client.delete(
            f"/projects/{project}/categories/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_categories_forbidden_user(self):
        """
        DELETE /projects/{project_id}/categories/{category_id} .

        - The route can be accessed by a student user.
        - The owner of the project must be the authenticated user.
        """
        project = 1
        category = 5
        response = self.student_offsite_client.delete(
            f"/projects/{project}/categories/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_categories_association_success(self):
        """
        DELETE /projects/{project_id}/categories/{category_id} .

        - The route can be accessed by a student user.
        - The authenticated user must be the president of the association owning the project.
        - The ProjectCategory link is deleted from db.
        - If the same ProjectCategory is attempted to be deleted, returns a HTTP 404.
        """
        project = 2
        category = 1
        old_project_edition_date = Project.visible_objects.get(id=project).edition_date
        response = self.student_president_client.delete(
            f"/projects/{project}/categories/{category}"
        )
        new_project_edition_date = Project.visible_objects.get(id=project).edition_date
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            0,
            len(ProjectCategory.objects.filter(project=project, category=category)),
        )
        self.assertNotEqual(old_project_edition_date, new_project_edition_date)

        response = self.student_president_client.delete(
            f"/projects/{project}/categories/{category}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
