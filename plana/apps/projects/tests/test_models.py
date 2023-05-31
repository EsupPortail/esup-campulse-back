"""List of tests done on projects models."""
from django.test import Client, TestCase

from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.users.models.user import User


class ProjectsModelsTests(TestCase):
    """Projects Models tests class."""

    fixtures = [
        "associations_association.json",
        "associations_activityfield.json",
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
        "projects_projectcomment.json",
        "projects_projectcommissiondate.json",
        "users_associationuser.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_category_model(self):
        """There's at least one category in the database."""
        category = Category.objects.first()
        self.assertEqual(str(category), category.name)

    def test_project_model(self):
        """There's at least one project in the database."""
        project = Project.visible_objects.first()
        self.assertEqual(str(project), project.name)

    def test_project_category_model(self):
        """There's at least one project category link in the database."""
        project_cat = ProjectCategory.objects.first()
        self.assertEqual(
            str(project_cat), f"{project_cat.project} {project_cat.category}"
        )

    def test_project_comment_model(self):
        """There's at least one project comment in the database."""
        project_comm = ProjectComment.objects.first()
        self.assertEqual(
            str(project_comm),
            f"{project_comm.user} {project_comm.project} : {project_comm.text}",
        )

    def test_project_commission_date_model(self):
        """There's at least one project commission date link in the database."""
        project_cd = ProjectCommissionDate.objects.first()
        self.assertEqual(
            str(project_cd), f"{project_cd.project} {project_cd.commission_date}"
        )

    def test_can_access_project_success_user(self):
        """
        Testing can_access_project Project helper
        - The project owner must be the authenticated user.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="etudiant-porteur@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_user(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="etudiant-asso-hors-site@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_success_association(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=2)
        user = User.objects.get(username="president-asso-site@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_association(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=2)
        user = User.objects.get(username="etudiant-asso-hors-site@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_forbidden_president(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=2)
        user = User.objects.get(username="etudiant-asso-site@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_success_commission(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be linked to a commission linked to a project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="membre-culture-actions@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_commission(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be linked to a commission linked to a project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="membre-fsdie-idex@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_success_institution(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be linked to an institution linked to a project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="gestionnaire-crous@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_institution(self):
        """
        Testing can_access_project Project helper
        - The authenticated user must be linked to an institution linked to a project.
        """
        user = User.objects.get(username="gestionnaire-uha@mail.tld")

        project = Project.visible_objects.get(id=1)
        self.assertFalse(user.can_access_project(project))

        project = Project.visible_objects.get(id=2)
        self.assertFalse(user.can_access_project(project))
