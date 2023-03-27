"""List of tests done on projects models."""
from django.test import Client, TestCase

from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.users.models.user import User


class ProjectsModelsTests(TestCase):
    """Projects Models tests class."""

    fixtures = [
        "associations_association.json",
        "associations_activityfield.json",
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissiondate.json",
        "users_associationusers.json",
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
        project = Project.objects.first()
        self.assertEqual(str(project), project.name)

    def test_project_category_model(self):
        """There's at least one project category link in the database."""
        project_cat = ProjectCategory.objects.first()
        self.assertEqual(
            str(project_cat), f"{project_cat.project} {project_cat.category}"
        )

    def test_project_commission_date_model(self):
        """There's at least one project commission date link in the database."""
        project_cd = ProjectCommissionDate.objects.first()
        self.assertEqual(
            str(project_cd), f"{project_cd.project} {project_cd.commission_date}"
        )

    def test_can_edit_project_success_user(self):
        """
        Testing can_update_project Project helper
        - The project owner must be the authenticated user.
        """
        project = Project.objects.get(pk=1)
        user = User.objects.get(username="etudiant-porteur@mail.tld")
        self.assertTrue(project.can_edit_project(user))

    def test_can_edit_project_forbidden_user(self):
        """
        Testing can_update_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.objects.get(pk=1)
        user = User.objects.get(username="etudiant-asso-hors-site@mail.tld")
        self.assertFalse(project.can_edit_project(user))

    def test_can_edit_project_success_association(self):
        """
        Testing can_update_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.objects.get(pk=2)
        user = User.objects.get(username="president-asso-site@mail.tld")
        self.assertTrue(project.can_edit_project(user))

    def test_can_edit_project_forbidden_association(self):
        """
        Testing can_update_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.objects.get(pk=2)
        user = User.objects.get(username="etudiant-asso-hors-site@mail.tld")
        self.assertFalse(project.can_edit_project(user))

    def test_can_edit_project_forbidden_president(self):
        """
        Testing can_update_project Project helper
        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.objects.get(pk=2)
        user = User.objects.get(username="etudiant-asso-site@mail.tld")
        self.assertFalse(project.can_edit_project(user))
