"""List of tests done on projects comments links views."""

import json

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment


class ProjectCommentLinksViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "tests/account_emailaddress.json",
        "associations_activityfield.json",
        "tests/associations_association.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/contents_setting.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_category.json",
        "tests/projects_project.json",
        "tests/projects_projectcomment.json",
        "tests/projects_projectcommissionfund.json",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
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
        cls.response = cls.student_president_client.post(url_login, data_student_president)

        cls.student_user_id = 9
        cls.student_user_name = "etudiant-porteur@mail.tld"
        cls.student_client = Client()
        data_student = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_client.post(url_login, data_student)

    def test_post_project_comments_anonymous(self):
        """
        POST /projects/comments .

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
        POST /projects/comments .

        - The route cannot be accessed by a student user.
        """
        post_data = {"project": 1, "text": "Forbidden comment"}
        response = self.student_offsite_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_comments_manager_wrong_status(self):
        """
        POST /projects/comments .

        - The route can be accessed by a manager.
        - Validated projects cannot receive a comment.
        """
        project_id = 1
        project = Project.visible_objects.get(id=project_id)
        project.project_status = "PROJECT_REJECTED"
        project.save()

        post_data = {
            "project": project_id,
            "text": "Project rejection.",
        }
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_comments_serializer_error(self):
        """
        POST /projects/comments .

        - The route can be accessed by a manager.
        - Serializer fields must be valid.
        """
        post_data = {"project": 1, "text": False}
        response = self.general_client.post("/projects/comments", data=post_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_comments_manager_success(self):
        """
        POST /projects/comments .

        - The route can be accessed by a manager.
        - The ProjectComment link is created in db.
        """
        self.assertFalse(len(mail.outbox))
        post_data = {"project": 1, "text": "Commentaire"}
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            1,
            len(ProjectComment.objects.filter(project=post_data["project"], text=post_data["text"])),
        )
        self.assertTrue(len(mail.outbox))
        post_data = {"project": 2, "text": "Autre Commentaire"}
        response = self.general_client.post("/projects/comments", post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            1,
            len(ProjectComment.objects.filter(project=post_data["project"], text=post_data["text"])),
        )

    def test_get_project_comments_by_id_anonymous(self):
        """
        GET /projects/{project_id}/comments .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/2/comments")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_comments_by_id_404(self):
        """
        GET /projects/{project_id}/comments .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999/comments")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_comments_by_id_forbidden_student(self):
        """
        GET /projects/{project_id}/comments .

        - A student user not owning the project cannot execute this request.
        """
        project_id = 2
        response = self.student_offsite_client.get(f"/projects/{project_id}/comments")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_comments_by_id_success(self):
        """
        GET /projects/{project_id}/comments .

        - The route can be accessed by a manager user.
        - The route can be accessed by a student user.
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

    def test_patch_project_comment_anonymous(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id} .

        - An anonymous user cannot execute this command.
        """
        patch_data = {"text": "Commentaire test"}
        response = self.client.patch("/projects/2/comments/1", data=patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_comment_not_found(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id} .

        - Comment must exist.
        """
        comment = 2
        project = 2
        patch_data = {"text": "Commentaire not found"}
        response = self.general_client.patch(
            f"/projects/{project}/comments/{comment}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_comment_forbidden(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id} .

        - A user without proper permissions cannot execute this command.
        - Manager must be from the correct institution.
        """
        comment = 1
        project = 2
        patch_data = {"text": "Commentaire forbidden"}
        response = self.student_client.patch(
            f"/projects/{project}/comments/{comment}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.institution_client.patch(
            f"/projects/{project}/comments/{comment}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_comments_manager_wrong_status(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id} .

        - The route can be accessed by a manager.
        - Comments cannot be updated on validated projects.
        """
        comment_id = 1
        project_id = 2
        project = Project.visible_objects.get(id=project_id)
        project.project_status = "PROJECT_REJECTED"
        project.save()

        patch_data = {"text": "Project rejected."}
        response = self.general_client.patch(
            f"/projects/{project_id}/comments/{comment_id}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_comments_serializer_error(self):
        """
        PATCH /projects/{id}/comments/{id} .

        - The route can be accessed by a manager.
        - Serializer fields must be valid.
        """
        patch_data = {"text": False}
        response = self.general_client.patch(
            "/projects/1/comments/1", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_comment_success(self):
        """
        PATCH /projects/{project_id}/comments/{comment_id} .

        - A user with proper permissions can execute this request.
        - The comment is correctly updated in db.
        """
        comment = 1
        project = 2
        patch_data = {"text": "Commentaire sent with success", "is_visible": True}
        response = self.general_client.patch(
            f"/projects/{project}/comments/{comment}",
            data=patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_comment = ProjectComment.objects.get(id=comment, project_id=project)
        self.assertEqual(updated_comment.text, "Commentaire sent with success")

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
        response = self.student_offsite_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.institution_client.delete(f"/projects/{project}/comments/{comment}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_comments_manager_wrong_status(self):
        """
        DELETE /projects/{project_id}/comments/{comment_id} .

        - The route can be accessed by a manager.
        - Comments cannot be deleted on validated projects.
        """
        comment_id = 1
        project_id = 2
        project = Project.visible_objects.get(id=project_id)
        project.project_status = "PROJECT_REJECTED"
        project.save()

        response = self.general_client.delete(f"/projects/{project_id}/comments/{comment_id}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
