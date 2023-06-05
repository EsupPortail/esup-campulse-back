import datetime

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate

User = get_user_model()


class AccountExpirationCommandTest(TestCase):
    fixtures = ['auth_group', 'mailtemplatevars', 'mailtemplates']

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', email='super@mail.tld', is_staff=True
        )
        self.user = User.objects.create_user('user', email='user@mail.tld')

    def test_current_users(self):
        self.superuser.last_login = timezone.now()
        self.superuser.save()
        self.user.last_login = timezone.now()
        self.user.save()
        call_command('cron_account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertEqual(User.objects.count(), 2)

    def test_old_staff_user(self):
        self.superuser.date_joined = timezone.now() - datetime.timedelta(days=1000)
        self.superuser.save()
        call_command('cron_account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())

    def test_account_without_connection_expiration_mail(self):
        self.user.date_joined = timezone.now() - datetime.timedelta(days=(365 - 31))
        self.user.save()
        call_command('cron_account_expiration')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_account_without_recent_connection_expiration_mail(self):
        self.user.last_login = timezone.now() - datetime.timedelta(days=(365 - 31))
        self.user.save()
        call_command('cron_account_expiration')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_account_without_connection_deletion(self):
        self.user.date_joined = timezone.now() - datetime.timedelta(days=1000)
        self.user.save()
        call_command('cron_account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())


class CommissionExpirationCommandTest(TestCase):
    """Test commission_expiration command."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_project.json",
        "projects_projectcommissiondate.json",
        "users_associationuser.json",
        "users_user.json",
    ]

    def test_no_expire_commission(self):
        """Don't remove ProjectCommissionDate if CommissionDate isn't expired."""
        expired_commission_id = 3
        old_project_commission_dates_count = ProjectCommissionDate.objects.filter(
            commission_date_id=expired_commission_id
        ).count()
        call_command("cron_commission_expiration")
        new_project_commission_dates_count = ProjectCommissionDate.objects.filter(
            commission_date_id=expired_commission_id
        ).count()
        self.assertEqual(
            old_project_commission_dates_count, new_project_commission_dates_count
        )

    def test_expire_commission(self):
        """Remove ProjectCommissionDate if CommissionDate is expired."""
        expired_commission_id = 3
        expired_commission = CommissionDate.objects.get(id=expired_commission_id)
        expired_commission.submission_date = datetime.datetime.strptime(
            "1993-12-25", "%Y-%m-%d"
        ).date()
        expired_commission.save()
        old_project_commission_dates_count = ProjectCommissionDate.objects.filter(
            commission_date_id=expired_commission_id
        ).count()
        call_command("cron_commission_expiration")
        new_project_commission_dates_count = ProjectCommissionDate.objects.filter(
            commission_date_id=expired_commission_id
        ).count()
        self.assertNotEqual(
            old_project_commission_dates_count, new_project_commission_dates_count
        )


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
        """An email is sent if password is 11 months old."""
        self.users.update(
            password_last_change_date=(self.today - datetime.timedelta(days=(365 - 31)))
        )
        call_command("cron_password_expiration")
        self.assertTrue(len(mail.outbox))

    def test_almost_password_reset_but_no_password_reset(self):
        """Nothing should change if password is 11.5 months old."""
        self.users.update(
            password_last_change_date=(self.today - datetime.timedelta(days=(365 - 45)))
        )
        call_command("cron_password_expiration")
        self.assertFalse(len(mail.outbox))

    def test_password_reset(self):
        """An email is sent if password is 12 months old."""
        self.users.update(
            password_last_change_date=(self.today - datetime.timedelta(days=365))
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
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
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
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "projects_projectcommissiondate.json",
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
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
                today - datetime.timedelta(days=30), datetime.datetime.min.time()
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
