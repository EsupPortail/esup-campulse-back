"""List of tests done on projects models."""
from unittest.mock import patch

from django.core import mail
from django.test import Client, TestCase, RequestFactory

from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.users.models.user import User


class ProjectsModelsTests(TestCase):
    """Projects Models tests class."""

    fixtures = [
        "tests/associations_association.json",
        "associations_activityfield.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/contents_setting.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_category.json",
        "tests/projects_project.json",
        "tests/projects_projectcategory.json",
        "tests/projects_projectcomment.json",
        "tests/projects_projectcommissionfund.json",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
        "mailtemplates",
        "mailtemplatevars",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = User.objects.create_user(username="admin", email="admin@test.com")

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
        self.assertEqual(str(project_cat), f"{project_cat.project} - {project_cat.category}")

    def test_project_comment_model(self):
        """There's at least one project comment in the database."""
        project_comm = ProjectComment.objects.first()
        self.assertEqual(str(project_comm), project_comm.text)

    def test_project_commission_fund_model(self):
        """There's at least one project commission fund link in the database."""
        project_cd = ProjectCommissionFund.objects.first()
        self.assertEqual(str(project_cd), f"{project_cd.project} - {project_cd.commission_fund}")

    def test_can_access_project_success_user(self):
        """
        Testing can_access_project Project helper.

        - The project owner must be the authenticated user.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="etudiant-porteur@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_user(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="etudiant-asso-hors-site@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_success_association(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=2)
        user = User.objects.get(username="president-asso-site@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_association(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=2)
        user = User.objects.get(username="etudiant-asso-hors-site@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_forbidden_president(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be the president of the association owning the project.
        """
        project = Project.visible_objects.get(id=2)
        user = User.objects.get(username="etudiant-asso-site@mail.tld")
        self.assertFalse(user.can_edit_project(project))

    def test_can_access_project_success_commission(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be linked to a fund linked to a project.
        """
        project = Project.visible_objects.get(id=5)
        user = User.objects.get(username="membre-culture-actions@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_commission(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be linked to a fund linked to a project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="membre-fsdie-idex@mail.tld")
        self.assertFalse(user.can_access_project(project))

    def test_can_access_project_success_institution(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be linked to an institution linked to a project.
        """
        project = Project.visible_objects.get(id=1)
        user = User.objects.get(username="gestionnaire-crous@mail.tld")
        self.assertTrue(user.can_access_project(project))

    def test_can_access_project_forbidden_institution(self):
        """
        Testing can_access_project Project helper.

        - The authenticated user must be linked to an institution linked to a project.
        """
        user = User.objects.get(username="gestionnaire-uha@mail.tld")

        project = Project.visible_objects.get(id=1)
        self.assertFalse(user.can_access_project(project))

        project = Project.visible_objects.get(id=2)
        self.assertFalse(user.can_access_project(project))

    def test_get_project_owner_data_user(self):
        project = Project.objects.get(id=1)
        data = project.get_project_owner_data()
        self.assertEqual(data["email"], "etudiant-porteur@mail.tld")
        self.assertEqual(data["address"], "  - , ")
        self.assertEqual(data["name"], "Porteur Étudiant")

    def test_get_project_owner_data_association(self):
        project = Project.objects.get(id=2)
        data = project.get_project_owner_data()
        self.assertEqual(data["email"], "president-asso-site@mail.tld")
        self.assertEqual(data["address"], "Université de Strasbourg (Le Portique, 3ème étage), Rue René Descartes Strasbourg - 67000, France")
        self.assertEqual(data["name"], "Association du Site Alsace")

        project.association_user = None
        project.save()
        new_data = project.get_project_owner_data()
        self.assertEqual(new_data["email"], "asso-site-alsace@unistra.fr")

    def test_can_transition_to_status_ok(self):
        project = Project.objects.get(id=1)
        self.assertTrue(project.can_transition_to_status(new_status=Project.ProjectStatus.PROJECT_PROCESSING))
        # Project should be able to roll back with a delta of 1
        project.project_status = Project.ProjectStatus.PROJECT_PROCESSING
        project.save()
        self.assertTrue(project.can_transition_to_status(new_status=Project.ProjectStatus.PROJECT_DRAFT_PROCESSED))

    def test_can_transition_to_status_forbidden(self):
        project = Project.objects.get(id=1)
        # Project should not be able to transition to a status with a delta > 1
        self.assertFalse(project.can_transition_to_status(new_status=Project.ProjectStatus.PROJECT_VALIDATED))

        # Project should not be able to transition from an archived status to another one
        project.project_status = Project.ProjectStatus.PROJECT_CANCELED
        project.save()
        self.assertFalse(project.can_transition_to_status(new_status=Project.ProjectStatus.PROJECT_REVIEW_PROCESSING))

        # Project should not be able to roll back from a non-rollbackable status
        project.project_status = Project.ProjectStatus.PROJECT_REVIEW_DRAFT
        project.save()
        self.assertFalse(project.can_transition_to_status(new_status=Project.ProjectStatus.PROJECT_VALIDATED))

    @patch.object(Project, "can_transition_to_status", return_value=True)
    def test_process_pcf_last_amount_earned_positive(self, mock_can_transition):
        project = Project.objects.get(id=10)
        pcf = ProjectCommissionFund.objects.get(pk=11)
        pcf.amount_earned = 100
        pcf.save()
        # Last PCF updated with positive amount earned
        project.process_project_pcf_amount_earned_status_update()
        mock_can_transition.assert_called_once_with(Project.ProjectStatus.PROJECT_REVIEW_DRAFT)
        project.refresh_from_db()
        self.assertEqual(project.project_status, Project.ProjectStatus.PROJECT_REVIEW_DRAFT)

    @patch.object(Project, "can_transition_to_status", return_value=True)
    def test_process_pcf_last_amount_earned_zero(self, mock_can_transition):
        project = Project.objects.get(id=10)
        pcf = ProjectCommissionFund.objects.get(pk=11)
        # Last PCF updated with an amount earned of zero
        pcf.amount_earned = 0
        pcf.save()
        project.process_project_pcf_amount_earned_status_update()
        mock_can_transition.assert_called_once_with(Project.ProjectStatus.PROJECT_CANCELED)
        project.refresh_from_db()
        self.assertEqual(project.project_status, Project.ProjectStatus.PROJECT_CANCELED)

    @patch.object(Project, "can_transition_to_status", return_value=True)
    def test_process_pcf_not_last_amount_earned(self, mock_can_transition):
        project_id = 10
        project = Project.objects.get(id=project_id)
        pcf = ProjectCommissionFund.objects.create(amount_asked=200, is_validated_by_admin=True, project_id=project.id, commission_fund_id=2)
        # Not the last pcf, do nothing
        pcf.amount_earned = 100
        pcf.save()
        project.process_project_pcf_amount_earned_status_update()
        mock_can_transition.assert_not_called()
        refreshed_other_project = Project.objects.get(id=project_id)
        self.assertEqual(refreshed_other_project.project_status, project.project_status)

    def test_process_pcf_admin_validation_ok(self):
        # If last pcf validated by admin, mail sent and project status updated accordingly
        project = Project.objects.get(id=3)
        pcf = ProjectCommissionFund.objects.get(pk=4)
        pcf.is_validated_by_admin = True
        pcf.save()

        project.process_project_pcf_admin_validation_status_update(request=self.request)
        project.refresh_from_db()
        self.assertEqual(project.project_status, Project.ProjectStatus.PROJECT_VALIDATED)
        self.assertEqual(len(mail.outbox), 1)

        # No double-mail sent if validated twice
        project.process_project_pcf_admin_validation_status_update(request=self.request)
        self.assertEqual(len(mail.outbox), 1)

    def test_process_pcf_admin_validation_fully_rejected(self):
        # If last pcf rejected by admin, mail sent and project status updated accordingly
        project = Project.objects.get(id=3)
        pcf = ProjectCommissionFund.objects.get(pk=4)
        pcf.is_validated_by_admin = False
        pcf.save()

        project.process_project_pcf_admin_validation_status_update(request=self.request)
        project.refresh_from_db()
        self.assertEqual(project.project_status, Project.ProjectStatus.PROJECT_REJECTED)
        self.assertEqual(len(mail.outbox), 1)

        # No double-mail sent if rejected twice
        project.process_project_pcf_admin_validation_status_update(request=self.request)
        self.assertEqual(len(mail.outbox), 1)

    def test_process_pcf_admin_validation_not_last(self):
        # If not last pcf validated by admin, no email sent and project status not updated yet
        project = Project.objects.get(id=4)
        pcf = ProjectCommissionFund.objects.get(pk=5)
        pcf.is_validated_by_admin = True
        pcf.save()

        project.process_project_pcf_admin_validation_status_update(request=self.request)
        project.refresh_from_db()
        self.assertEqual(project.project_status, Project.ProjectStatus.PROJECT_PROCESSING)
        self.assertEqual(len(mail.outbox), 0)
