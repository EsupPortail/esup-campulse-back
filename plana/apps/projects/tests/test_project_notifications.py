"""Unittests for projects notifications."""
import datetime
from unittest.mock import patch, ANY

from django.utils import timezone
from django.test import Client, TestCase, RequestFactory

from plana.apps.commissions.models import Commission
from plana.apps.contents.models import Content
from plana.apps.history.models import History
from plana.apps.projects import notifications
from plana.apps.projects.models import ProjectCommissionFund, ProjectComment, Project
from plana.apps.users.models.user import User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class ProjectPCFNotificationsTestCase(TestCase):
    """Tests class for project PCF notifications."""

    fixtures = [
        "tests/associations_association.json",
        "associations_activityfield.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/contents_setting.json",
        "tests/contents_content.json",
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

    def test_build_pcf_notification_data_empty_template(self):
        request = self.request
        pcf = ProjectCommissionFund.objects.get(pk=10)

        result = notifications.build_pcf_notification_attachment_data(
            request=request,
            pcf=pcf,
            template_path="",
            content_code="NOTIFICATION_Culture-ActionS_ATTRIBUTION",
            from_admin=False
        )

        assert result is None

    def test_build_pcf_notification_data_from_admin(self):
        request = self.request
        pcf = ProjectCommissionFund.objects.get(pk=10)

        result = notifications.build_pcf_notification_attachment_data(
            request=request,
            pcf=pcf,
            template_path="Culture-ActionS/attribution.html",
            content_code="NOTIFICATION_CULTURE-ACTIONS_ATTRIBUTION",
            from_admin=True
        )

        self.assertNotIn("pcf_obj", result)

    def test_build_pcf_notification_data_not_from_admin(self):
        request = self.request
        pcf = ProjectCommissionFund.objects.get(pk=10)
        content_code = "NOTIFICATION_CULTURE-ACTIONS_ATTRIBUTION"

        result = notifications.build_pcf_notification_attachment_data(
            request=request,
            pcf=pcf,
            template_path="Culture-ActionS/attribution.html",
            content_code=content_code,
            from_admin=False
        )

        self.assertIn("pcf_obj", result)
        context = result["context_attach"]
        self.assertEqual(context["project_name"], pcf.project.name)
        self.assertEqual(context["content"], Content.objects.get(code=content_code))
        # No comment on this project for now
        self.assertEqual(context["comment"], "")

        # Check on comment when there's one
        ProjectComment.objects.create(project=pcf.project, text="Testing", user=self.request.user)
        ProjectComment.objects.create(project=pcf.project, text="Testing 2", user=self.request.user, creation_date=timezone.now() + datetime.timedelta(seconds=1))
        result_with_comment = notifications.build_pcf_notification_attachment_data(
            request=request,
            pcf=pcf,
            template_path="Culture-ActionS/attribution.html",
            content_code=content_code,
            from_admin=False
        )
        context = result_with_comment["context_attach"]
        self.assertEqual(context["comment"], "Testing 2")

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.notifications.build_pcf_notification_attachment_data", wraps=notifications.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_wrong_notification_type(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert notifications.send_pcf_notification_mail_with_attachments(
            request=self.request,
            pcf=pcf,
            notification_type="TEST",
            from_admin=False
        ) is None
        wrap_build_attachment.assert_not_called()
        wrap_send_mail.assert_not_called()

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.notifications.build_pcf_notification_attachment_data", wraps=notifications.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_attribution(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert notifications.send_pcf_notification_mail_with_attachments(
            request=self.request,
            pcf=pcf,
            notification_type="ATTRIBUTION",
            from_admin=False
        ) is None
        self.assertEqual(wrap_build_attachment.call_count, 2)
        wrap_send_mail.assert_called_once_with(
            from_=ANY,
            to_=pcf.project.get_project_owner_data().get("email"),
            cc_=pcf.project.get_project_default_manager_emails(pcf.commission_fund.fund_id),
            subject=ANY,
            message=ANY,
            temp_attachments=ANY
        )

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.notifications.build_pcf_notification_attachment_data", wraps=notifications.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_postpone(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert notifications.send_pcf_notification_mail_with_attachments(
            request=self.request,
            pcf=pcf,
            notification_type="POSTPONE",
            from_admin=False
        ) is None
        self.assertEqual(wrap_build_attachment.call_count, 1)
        wrap_send_mail.assert_called_once_with(
            from_=ANY,
            to_=pcf.project.get_project_owner_data().get("email"),
            cc_=[],
            subject=ANY,
            message=ANY,
            temp_attachments=ANY
        )

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.notifications.build_pcf_notification_attachment_data", wraps=notifications.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_from_admin(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert notifications.send_pcf_notification_mail_with_attachments(
            request=self.request,
            pcf=pcf,
            notification_type="REJECTION",
            from_admin=True
        ) is None
        self.assertEqual(wrap_build_attachment.call_count, 1)
        wrap_send_mail.assert_called_once_with(
            from_=ANY,
            to_=self.request.user.email,
            cc_=[],
            subject=ANY,
            message=ANY,
            temp_attachments=ANY
        )


class ProjectStatusNotificationsTestCase(TestCase):
    """Tests class for project PCF notifications."""

    fixtures = [
        "tests/associations_association.json",
        "associations_activityfield.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/contents_setting.json",
        "tests/contents_content.json",
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

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    def test_bearer_association_project_processing_status(self, mock_send_mail):
        """Assert that a project processing from a bearer sends correct email"""
        project = Project.objects.get(pk=4)
        expected_template = MailTemplate.objects.get(code="MANAGER_PROJECT_ASSOCIATION_CREATION")

        notifications.send_project_status_update_notification(self.request, project)

        mock_send_mail.assert_called_once()
        kwargs = mock_send_mail.call_args.kwargs
        self.assertEqual(kwargs["to_"], project.get_project_default_manager_emails())
        self.assertIn(expected_template.subject.split("{{")[0].strip(), kwargs["subject"])

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    def test_validator_project_validated_status_without_bcc(self, mock_send_mail):
        """Assert that a project validated by a validator sends correct email and creates history entry"""
        project = Project.objects.get(pk=10)
        initial_history_count = History.objects.filter(project_id=project.id,action_title="PROJECT_VALIDATED",).count()

        notifications.send_project_status_update_notification(self.request, project)

        self.assertEqual(
            History.objects.filter(project_id=project.id, action_title="PROJECT_VALIDATED").count(),
            initial_history_count + 1,
        )
        mock_send_mail.assert_called_once()
        self.assertEqual(mock_send_mail.call_args.kwargs["to_"], project.get_project_owner_data().get("email"))
        # Only when the commission is tomorrow
        self.assertEqual(mock_send_mail.call_args.kwargs["bcc_"], [])

    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    @patch("plana.apps.commissions.models.Commission.get_fund_members_emails")
    def test_validator_project_validated_status_with_bcc(self, mock_emails, mock_send_mail):
        """
        Assert that a project validated by a validator sends correct email and creates history entry
        with bcc if the commission is tomorrow
        """
        fake_emails = ["test@test.fr", "test2@test.fr"]
        mock_emails.return_value = fake_emails
        Commission.objects.filter(pk=1).update(commission_date=timezone.localdate() + datetime.timedelta(days=1))
        # If last pcf validated by admin, mail sent and project status updated accordingly
        project = Project.objects.get(pk=10)
        initial_history_count = History.objects.filter(project_id=project.id,action_title="PROJECT_VALIDATED",).count()

        notifications.send_project_status_update_notification(self.request, project)

        self.assertEqual(
            History.objects.filter(project_id=project.id, action_title="PROJECT_VALIDATED").count(),
            initial_history_count + 1,
        )
        mock_send_mail.assert_called_once()
        self.assertEqual(mock_send_mail.call_args.kwargs["to_"], project.get_project_owner_data().get("email"))
        self.assertEqual(mock_send_mail.call_args.kwargs["bcc_"], fake_emails)


    @patch("plana.apps.projects.notifications.send_mail", wraps=send_mail)
    def test_project_status_without_notification(self, mock_send_mail):
        """A status update that doesn't trigger bearer or validator email should do nothing"""
        project = Project.objects.get(pk=1)

        notifications.send_project_status_update_notification(self.request, project)
        mock_send_mail.assert_not_called()

    @patch("plana.apps.projects.notifications.send_mail", side_effect=RuntimeError("SMTP down"))
    def test_project_status_notification_mail_error(self, mock_send_mail):
        """An email sending error should create an exception logger without raising the exception"""
        project = Project.objects.get(pk=9)

        with self.assertLogs(level="ERROR") as logs:
            notifications.send_project_status_update_notification(self.request, project)

        mock_send_mail.assert_called_once()
        self.assertTrue(any("Failed to send status update notification" in msg for msg in logs.output))
