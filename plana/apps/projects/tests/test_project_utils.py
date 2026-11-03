"""Unittests for projects utils."""
import datetime
from unittest.mock import patch, ANY

from django.utils import timezone
from django.test import Client, TestCase, RequestFactory

from plana.apps.contents.models import Content
from plana.apps.projects import utils
from plana.apps.projects.models import ProjectCommissionFund, ProjectComment
from plana.apps.users.models.user import User
from plana.utils import send_mail


class ProjectsUtilsTestCase(TestCase):
    """Projects Utils tests class."""

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

        result = utils.build_pcf_notification_attachment_data(
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

        result = utils.build_pcf_notification_attachment_data(
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

        result = utils.build_pcf_notification_attachment_data(
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
        result_with_comment = utils.build_pcf_notification_attachment_data(
            request=request,
            pcf=pcf,
            template_path="Culture-ActionS/attribution.html",
            content_code=content_code,
            from_admin=False
        )
        context = result_with_comment["context_attach"]
        self.assertEqual(context["comment"], "Testing 2")

    @patch("plana.apps.projects.utils.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.utils.build_pcf_notification_attachment_data", wraps=utils.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_wrong_notification_type(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert utils.send_pcf_notification_mail_with_attachments(
            request=self.request,
            pcf=pcf,
            notification_type="TEST",
            from_admin=False
        ) is None
        wrap_build_attachment.assert_not_called()
        wrap_send_mail.assert_not_called()

    @patch("plana.apps.projects.utils.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.utils.build_pcf_notification_attachment_data", wraps=utils.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_attribution(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert utils.send_pcf_notification_mail_with_attachments(
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

    @patch("plana.apps.projects.utils.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.utils.build_pcf_notification_attachment_data", wraps=utils.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_postpone(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert utils.send_pcf_notification_mail_with_attachments(
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

    @patch("plana.apps.projects.utils.send_mail", wraps=send_mail)
    @patch("plana.apps.projects.utils.build_pcf_notification_attachment_data", wraps=utils.build_pcf_notification_attachment_data)
    def test_send_pcf_notification_mail_from_admin(self, wrap_build_attachment, wrap_send_mail):
        pcf = ProjectCommissionFund.objects.get(pk=10)
        assert utils.send_pcf_notification_mail_with_attachments(
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
