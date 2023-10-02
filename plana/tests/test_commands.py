"""Test commands in management folder."""
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import Commission, CommissionFund
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund

User = get_user_model()


class AccountExpirationCommandTest(TestCase):
    """Test account_expiration command."""

    fixtures = ['auth_group', 'mailtemplatevars', 'mailtemplates']

    def setUp(self):
        """Cache users."""
        self.superuser = User.objects.create_superuser('superuser', email='super@mail.tld', is_staff=True)
        self.user = User.objects.create_user('user', email='user@mail.tld')

    def test_current_users(self):
        """Users should not be deleted if login is recent."""
        self.superuser.last_login = timezone.now()
        self.superuser.save()
        self.user.last_login = timezone.now()
        self.user.save()
        call_command('cron_account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertEqual(User.objects.count(), 2)

    def test_old_staff_user(self):
        """Staff users shouldn't be deleted."""
        self.superuser.date_joined = timezone.now() - datetime.timedelta(days=1000)
        self.superuser.save()
        call_command('cron_account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())

    def test_account_without_connection_expiration_mail(self):
        """User without login should be warned."""
        self.user.date_joined = timezone.now() - datetime.timedelta(
            days=settings.CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION_WARNING
        )
        self.user.save()
        call_command('cron_account_expiration')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_account_without_recent_connection_expiration_mail(self):
        """User without recent login should be warned."""
        self.user.last_login = timezone.now() - datetime.timedelta(
            days=settings.CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION_WARNING
        )
        self.user.save()
        call_command('cron_account_expiration')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_account_without_connection_deletion(self):
        """User without recent login and warned should be deleted."""
        self.user.date_joined = timezone.now() - datetime.timedelta(days=1000)
        self.user.save()
        call_command('cron_account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())


class AssociationExpirationCommandTest(TestCase):
    """Test association_expiration command."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
    ]

    def setUp(self):
        """Cache all associations."""
        self.associations = Association.objects.all()
        self.today = datetime.date.today()

    def test_no_association_expiration(self):
        """Nothing should change if no charter expires."""
        call_command("cron_association_expiration")
        self.assertFalse(len(mail.outbox))

    def test_almost_association_expiration(self):
        """An email is sent if charter expires in WARNING days."""
        self.associations.update(
            charter_date=(
                self.today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION_WARNING)
            )
        )
        call_command("cron_association_expiration")
        self.assertTrue(len(mail.outbox))

    def test_almost_association_expiration_but_no_association_expiration(self):
        """Nothing should change if charter expires in WARNING - 1 days."""
        self.associations.update(
            charter_date=(
                self.today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION_WARNING - 1)
            )
        )
        call_command("cron_association_expiration")
        self.assertFalse(len(mail.outbox))

    def test_association_expiration(self):
        """Association charter status expires today."""
        self.assertNotEqual(self.associations[0].charter_status, "CHARTER_EXPIRED")
        self.associations.update(
            charter_date=(self.today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION))
        )
        call_command("cron_association_expiration")
        self.assertEqual(self.associations[0].charter_status, "CHARTER_EXPIRED")


class CommissionExpirationCommandTest(TestCase):
    """Test commission_expiration command."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "commissions_fund.json",
        "commissions_commission.json",
        "commissions_commissionfund.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "projects_projectcommissionfund.json",
        "users_associationuser.json",
        "users_user.json",
    ]

    def test_no_expire_commission(self):
        """Don't remove ProjectCommissionFund if Commission isn't expired."""
        expired_commission_id = 2
        old_project_commission_funds_count = ProjectCommissionFund.objects.filter(
            commission_fund_id__in=CommissionFund.objects.filter(commission_id=expired_commission_id).values("id")
        ).count()
        call_command("cron_commission_expiration")
        new_project_commission_funds_count = ProjectCommissionFund.objects.filter(
            commission_fund_id__in=CommissionFund.objects.filter(commission=expired_commission_id).values("id")
        ).count()
        self.assertEqual(old_project_commission_funds_count, new_project_commission_funds_count)

    def test_expire_commission(self):
        """Remove ProjectCommissionFund if Commission is expired."""
        expired_commission_id = 2
        expired_commission = Commission.objects.get(id=expired_commission_id)
        expired_commission.submission_date = datetime.datetime.strptime("1993-12-25", "%Y-%m-%d").date()
        expired_commission.save()
        self.assertTrue(expired_commission.is_open_to_projects)

        old_project_commission_funds_count = ProjectCommissionFund.objects.filter(
            commission_fund_id__in=CommissionFund.objects.filter(commission_id=expired_commission_id).values(
                "commission_id"
            )
        ).count()
        call_command("cron_commission_expiration")
        new_project_commission_funds_count = ProjectCommissionFund.objects.filter(
            commission_fund_id__in=CommissionFund.objects.filter(commission=expired_commission_id).values("id")
        ).count()
        self.assertNotEqual(old_project_commission_funds_count, new_project_commission_funds_count)

        expired_commission = Commission.objects.get(id=expired_commission_id)
        self.assertFalse(expired_commission.is_open_to_projects)


class DocumentExpirationCommandTest(TestCase):
    # TODO Rewrite all tests with expiration_day checks instead of days_before_expiration.
    """Test document_expiration command."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "commissions_fund.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "users_associationuser.json",
        "users_user.json",
    ]

    def setUp(self):
        """Cache all document uploads."""
        self.days_before_expiration = 365
        self.expiration_day = "08-31"
        self.document_uploads = DocumentUpload.objects.filter(
            document_id__in=Document.objects.filter(expiration_day=self.expiration_day)
        )
        for document_upload in self.document_uploads:
            document_upload.expiration_day = None
            document_upload.days_before_expiration = f"{self.days_before_expiration} days"
            document_upload.save()
        self.today = datetime.date.today()

    def test_no_document_upload_expiration(self):
        """Nothing should change if no document upload expires."""
        call_command("cron_document_expiration")
        # self.assertFalse(len(mail.outbox))

    def test_almost_document_upload_expiration(self):
        """An email is sent if document upload expires in WARNING days."""
        self.document_uploads.update(
            validated_date=(
                self.today
                - datetime.timedelta(
                    days=(self.days_before_expiration - settings.CRON_DAYS_DELAY_BEFORE_DOCUMENT_EXPIRATION_WARNING)
                )
            )
        )
        call_command("cron_document_expiration")
        # self.assertTrue(len(mail.outbox))

    def test_almost_document_upload_expiration_but_no_document_upload_expiration(self):
        """Nothing should change if document expires in WARNING - 1 days."""
        self.document_uploads.update(
            validated_date=(
                self.today
                - datetime.timedelta(
                    days=(
                        self.days_before_expiration - settings.CRON_DAYS_DELAY_BEFORE_DOCUMENT_EXPIRATION_WARNING - 1
                    )
                )
            )
        )
        call_command("cron_document_expiration")
        # self.assertFalse(len(mail.outbox))

    def test_document_upload_expiration(self):
        """Document upload expires today."""
        initial_document_uploads_count = self.document_uploads.count()
        self.document_uploads.update(
            validated_date=(self.today - datetime.timedelta(days=self.days_before_expiration))
        )
        call_command("cron_document_expiration")
        # self.assertNotEqual(self.document_uploads.count(), initial_document_uploads_count)


class GOAExpirationCommandTest(TestCase):
    """Test association_expiration command."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "commissions_fund.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    def setUp(self):
        """Cache all associations."""
        self.associations = Association.objects.all()
        self.today = datetime.date.today()

    def test_no_goa_expiration(self):
        """Nothing should change if no GOA date expires."""
        self.associations.update(last_goa_date=self.today)
        call_command("cron_goa_expiration")
        self.assertFalse(len(mail.outbox))

    def test_goa_expiration(self):
        """GOA date expires this month."""
        call_command("cron_goa_expiration")
        self.assertTrue(len(mail.outbox))


class PasswordExpirationCommandTest(TestCase):
    """Test password_expiration command."""

    fixtures = [
        "mailtemplates",
        "mailtemplatevars",
        "users_user.json",
    ]

    def setUp(self):
        """Cache all users."""
        self.users = User.objects.all()
        self.today = datetime.date.today()

    def test_no_password_reset(self):
        """Nothing should change if password was changed today."""
        self.users.update(password_last_change_date=self.today)
        call_command("cron_password_expiration")
        self.assertFalse(len(mail.outbox))

    def test_almost_password_reset(self):
        """An email is sent if password is WARNING months old."""
        self.users.update(
            password_last_change_date=(
                self.today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_PASSWORD_EXPIRATION_WARNING)
            )
        )
        call_command("cron_password_expiration")
        self.assertTrue(len(mail.outbox))

    def test_almost_password_reset_but_no_password_reset(self):
        """Nothing should change if password is WARNING + 1 months old."""
        self.users.update(
            password_last_change_date=(
                self.today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_PASSWORD_EXPIRATION_WARNING + 1)
            )
        )
        call_command("cron_password_expiration")
        self.assertFalse(len(mail.outbox))

    def test_password_reset(self):
        """An email is sent if password is EXPIRATION months old."""
        self.users.update(
            password_last_change_date=(
                self.today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_PASSWORD_EXPIRATION)
            )
        )
        call_command("cron_password_expiration")
        self.assertTrue(len(mail.outbox))


class ProjectExpirationCommandTest(TestCase):
    """Test project_expiration command."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_fund.json",
        "commissions_commission.json",
        "commissions_commissionfund.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "users_associationuser.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    def test_no_project_expiration(self):
        """Nothing should change if all projects are up to date."""
        project_to_delete = Project.objects.get(id=9)
        project_to_delete.save()

        old_projects_cnt = Project.objects.all().count()
        call_command("cron_project_expiration")
        new_projects_cnt = Project.objects.all().count()
        self.assertEqual(old_projects_cnt, new_projects_cnt)

    def test_project_expiration(self):
        """Delete a too old project."""
        old_projects_cnt = Project.objects.all().count()
        call_command("cron_project_expiration")
        new_projects_cnt = Project.objects.all().count()
        self.assertNotEqual(old_projects_cnt, new_projects_cnt)


class ReviewExpirationCommandTest(TestCase):
    """Test review_expiration command."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_fund.json",
        "commissions_commission.json",
        "commissions_commissionfund.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "projects_projectcommissionfund.json",
        "users_associationuser.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    def test_no_review_expiration(self):
        """Nothing should change if review should not be sent."""
        call_command("cron_review_expiration")
        self.assertFalse(len(mail.outbox))

    def test_review_expiration(self):
        """An email is sent if review should be sent."""
        today = datetime.date.today()
        mail_sending_due_date = timezone.make_aware(
            datetime.datetime.combine(
                today - datetime.timedelta(days=settings.CRON_DAYS_DELAY_AFTER_REVIEW_EXPIRATION),
                datetime.datetime.min.time(),
            )
        )
        projects_needing_review = Project.visible_objects.filter(id__in=[1, 2])
        for project_needing_review in projects_needing_review:
            project_needing_review.planned_start_date = mail_sending_due_date
            project_needing_review.planned_end_date = mail_sending_due_date
            project_needing_review.project_status = "PROJECT_REVIEW_DRAFT"
            project_needing_review.save()
        call_command("cron_review_expiration")
        self.assertTrue(len(mail.outbox))
