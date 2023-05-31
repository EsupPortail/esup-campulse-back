"""List of tests done on projects comments links views"""
import json

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.users.models import GroupInstitutionFundUser


class ProjectCommentLinksViewsTests(TestCase):
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
        "mailtemplates",
        "mailtemplatevars",
        "projects_category.json",
        "projects_project.json",
        "projects_projectcomment.json",
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

        cls.student_user_id = 9
        cls.student_user_name = "etudiant-porteur@mail.tld"
        cls.student_client = Client()
        data_student = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_client.post(url_login, data_student)

    def test_get_project_comments_anonymous(self):
        """
        GET /projects/comments .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/comments")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_comments_student(self):
        """
        GET /projects/comments

        - A student user gets comments where projects rights are OK.
        """
        response = self.student_offsite_client.get("/projects/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_comments_institution_manager(self):
        """
        GET /projects/comments

        - An institution manager user gets project comments for correct projects.
        """
        response = self.institution_client.get("/projects/comments")
        user_institution_ids = Institution.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(
                user_id=self.manager_institution_user_id
            ).values_list("institution_id")
        )
        project_comments_cnt = ProjectComment.objects.filter(
            project_id__in=Project.visible_objects.filter(
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

        - A general manager user gets all project comments.
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

    def test_post_project_comments_anonymous(self):
        """
        POST /projects/comments

        - An anonymous user cannot execute this command.
        """

        response = self.client.post("/projects/comments", {"name": "Testing anonymous"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_project_comments_not_found(self):
        """
        POST /projects/comments .

        - The project must exist.
        """
        post_data = {
            "project": 99999,
            "text": "Ce commentaire n'est pas censé exister.",
        }
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_comments_forbidden_user(self):
        """
        POST /projects/comments

        - The route cannot be accessed by a student user.
        """
        post_data = {"project": 1, "text": "Le chiffre 6 c'est comme saucisse"}
        response = self.student_offsite_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_comments_manager_success(self):
        """
        POST /projects/comments

        - The route can be accessed by a manager.
        - The ProjectComment link is created in db.
        """
        self.assertFalse(len(mail.outbox))
        post_data = {"project": 1, "text": "Commentaire"}
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            1,
            len(
                ProjectComment.objects.filter(
                    project=post_data["project"], text=post_data["text"]
                )
            ),
        )
        self.assertTrue(len(mail.outbox))
        post_data = {"project": 2, "text": "Autre Commentaire"}
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            1,
            len(
                ProjectComment.objects.filter(
                    project=post_data["project"], text=post_data["text"]
                )
            ),
        )

    def test_get_project_comments_by_id_anonymous(self):
        """
        GET /projects/{project_id}/comments

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/2/comments")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_comments_by_id_404(self):
        """
        GET /projects/{project_id}/comments

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/comments")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_comments_by_id_forbidden_student(self):
        """
        GET /projects/{project_id}/comments

        - A student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.get("/projects/2/comments")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_comments_by_id(self):
        """
        GET /projects/{project_id}/comments

        - The route can be accessed by a manager user and by a student user.
        - Correct projects comments are returned.
        """
        project_id = 2

        project_test_cnt = ProjectComment.objects.filter(project_id=project_id).count()
        response = self.general_client.get(f"/projects/{project_id}/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

        project_test_cnt = ProjectComment.objects.filter(project_id=project_id).count()
        response = self.student_president_client.get(f"/projects/{project_id}/comments")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), project_test_cnt)

    def test_get_project_comment_by_id_405(self):
        """
        GET /projects/{project_id}/comments/{comment_id}

        - Always returns a 405 no matter which user tries to access it.
        """
        project = 2
        comment = 1
        response = self.client.get(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_project_comment_by_id_405(self):
        """
        PUT /projects/{project_id}/comments/{comment_id}

        - Always returns a 405 no matter which user tries to access it.
        """
        data = {"text": "Commentaire test"}
        response = self.client.put("/projects/2/comments/1", data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_comment_anonymous(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id}

        - An anonymous user cannot execute this command.
        """
        patch_data = {"text": "Commentaire test"}
        response = self.client.patch(
            "/projects/2/comments/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_comment_not_found(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id}

        - Comment must exist.
        """
        patch_data = {"text": "Commentaire not found"}
        response = self.general_client.patch(
            "/projects/2/comments/2", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_comment_forbidden(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id}

        - A user without proper permissions cannot execute this command.
        - Manager must be from the correct institution.
        """
        patch_data = {"text": "Commentaire forbidden"}
        response = self.student_client.patch(
            "/projects/2/comments/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.institution_client.patch(
            "/projects/2/comments/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_comment_success(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id}

        - A user with proper permissions can execute this command.
        """
        patch_data = {"text": "Commentaire sent with success"}
        response = self.general_client.patch(
            "/projects/2/comments/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        DELETE /projects/{project_id}/comments/{category_id} .

        - The route cannot be accessed by a student user.
        - Manager must be from the correct institution.
        """
        project = 2
        comment = 1
        response = self.student_offsite_client.delete(
            f"/projects/{project}/comments/{comment}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.institution_client.delete(
            f"/projects/{project}/comments/{comment}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_comments_success(self):
        """
        DELETE /projects/{project_id}/comments/{comment_id} .

        - The route can be accessed by a manager user.
        - Comment is correctly deleted.
        """
        project = 2
        comment = 1
        response = self.general_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            0,
            len(ProjectComment.objects.filter(project=project, id=comment)),
        )
        response = self.general_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
