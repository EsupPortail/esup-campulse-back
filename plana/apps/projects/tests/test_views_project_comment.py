"""List of tests done on projects comments links views"""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.users.models import GroupInstitutionCommissionUser


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
        "projects_projectcomment.json",
        "projects_projectcommissiondate.json",
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
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

    def test_get_project_comments_anonymous(self):
        """
        GET /projects/comments .

        - An anonymous user cannot execute this request
        """
        response = self.client.get("/projects/comments")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_comments_student(self):
        """
        GET /projects/comments

        - A student user gets comments where projects rights are OK
        """
        response = self.student_offsite_client.get("/projects/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_comments_institution_manager(self):
        """
        GET /projects/comments

        - An institution manager user gets project comments for correct projects
        """
        response = self.institution_client.get("/projects/comments")
        user_institution_ids = Institution.objects.filter(
            id__in=GroupInstitutionCommissionUser.objects.filter(
                user_id=self.manager_institution_user_id
            ).values_list("institution_id")
        )
        project_comments_cnt = ProjectComment.objects.filter(
            project_id__in=Project.objects.filter(
                association_id__in=Association.objects.filter(
                    institution_id__in=user_institution_ids
                ).values_list("id")
            )
        ).count()

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), project_comments_cnt)

    def test_get_project_comments_manager(self):
        """
        GET /projects/comments .

        - A general manager user gets all project categories.
        - project_id argument filters by Project ID.
        """
        response = self.general_client.get("/projects/comments")
        projects_categories_cnt = ProjectComment.objects.all().count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_categories_cnt)

        response = self.general_client.get("/projects/comments?project_id=2")
        projects_categories_cnt = ProjectComment.objects.filter(project_id=2).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_categories_cnt)

    def test_post_project_comment_not_found(self):
        """
        POST /projects/comments .

        - The route can be accessed by a manager.
        - The project must exist.
        """
        post_data = {
            "project": 999,
            "text": "Ce commentaire n'est pas censé exister.",
        }
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_comment_forbidden_user(self):
        """
        POST /projects/comments

        - The route cannot be accessed by a student user
        """
        post_data = {"project": 1, "text": "Le chiffre 6 c'est comme saucisse"}
        response = self.student_offsite_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_comments_by_id_anonymous(self):
        """
        GET /projects/{project_id}/comments

        - An anonymous user cannot execute this request
        """
        response = self.client.get("/projects/1/comments")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_comments_by_id_404(self):
        """
        GET /projects/{project_id}/comments

        - The route returns a 404 if a wrong project id is given
        """
        response = self.general_client.get("/projects/99999/comments")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_comments_by_id_403(self):
        """
        GET /projects/{project_id}/comments

        - A student user not owning the project cannot execute this request
        """
        response = self.student_offsite_client.get("/projects/2/comments")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_comments_by_id(self):
        """
        GET /projects/{project_id}/comments

        - The route can be accessed by a manager user and by a student user
        - Correct projects comments are returned
        """
        project_id = 1
        project_test_cnt = ProjectComment.objects.filter(project_id=project_id).count()
        response = self.general_client.get(f"/projects/{project_id}/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

        project_id = 2
        project_test_cnt = ProjectComment.objects.filter(project_id=project_id).count()
        response = self.student_president_client.get(f"/projects/{project_id}/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

    def test_delete_project_comments_anonymous(self):
        """
        DELETE /projects/{project_id}/comments/{comment_id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/1/comments/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_comments_not_found(self):
        """
        DELETE /projects/{project_id}/comments/{comment_id} .

        - The project must exist.
        """
        project = 999
        comment = 1
        response = self.general_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_comments_forbidden_user(self):
        """
        DELETE /projects/{project_id}/categories/{category_id} .

        - The route cannot be accessed by a student user.
        """
        project = 1
        comment = 5
        response = self.student_offsite_client.delete(
            f"/projects/{project}/comments/{comment}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_comments_success(self):
        """
        DELETE /projects/{project_id}/comments/{comment_id} .

        - The route cannot be accessed by a manager user.
        - Comment is correctly deleted.
        """
        project = 2
        comment = 1
        response = self.general_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            0,
            len(ProjectComment.objects.filter(project=project, text=comment)),
        )
        response = self.general_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
