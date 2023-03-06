import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

User = get_user_model()


class AccountExpirationCommandTest(TestCase):
    fixtures = ['auth_group', 'mailtemplatevars', 'mailtemplates']

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', email='super@mail.tld'
        )
        self.group_user = User.objects.create_user('groupuser', email='group@mail.tld')
        self.group_user.groups.add(Group.objects.first())

    def test_current_users(self):
        self.superuser.last_login = timezone.now()
        self.superuser.save()
        self.group_user.last_login = timezone.now()
        self.group_user.save()
        call_command('account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertEqual(User.objects.count(), 2)

    def test_old_user_without_groups(self):
        self.superuser.date_joined = timezone.now() - datetime.timedelta(days=1000)
        self.superuser.save()
        call_command('account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())

    def test_account_without_connection_expiration_mail(self):
        self.group_user.date_joined = timezone.now() - datetime.timedelta(
            days=(2 * 365 - 31)
        )
        self.group_user.save()
        call_command('account_expiration')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(pk=self.group_user.pk).exists())

    def test_account_without_recent_connection_expiration_mail(self):
        self.group_user.last_login = timezone.now() - datetime.timedelta(
            days=(2 * 365 - 31)
        )
        self.group_user.save()
        call_command('account_expiration')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(pk=self.group_user.pk).exists())

    def test_account_without_connection_deletion(self):
        self.group_user.date_joined = timezone.now() - datetime.timedelta(days=1000)
        self.group_user.save()
        call_command('account_expiration')
        self.assertFalse(len(mail.outbox))
        self.assertFalse(User.objects.filter(pk=self.group_user.pk).exists())


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
        """Nothing should change if password was changed recently."""
        self.users.update(password_last_change_date=self.today)
        call_command("password_expiration")
        self.assertFalse(len(mail.outbox))

    def test_almost_password_reset(self):
        """Nothing should change if password was changed recently."""
        self.users.update(
            password_last_change_date=(self.today - datetime.timedelta(days=(365 - 31)))
        )
        call_command("password_expiration")
        self.assertTrue(len(mail.outbox))

    def test_almost_password_reset_but_no_password_reset(self):
        """Nothing should change if password was changed recently."""
        self.users.update(
            password_last_change_date=(self.today - datetime.timedelta(days=(365 - 45)))
        )
        call_command("password_expiration")
        self.assertFalse(len(mail.outbox))

    def test_password_reset(self):
        """Nothing should change if password was changed recently."""
        self.users.update(
            password_last_change_date=(self.today - datetime.timedelta(days=365))
        )
        call_command("password_expiration")
        self.assertTrue(len(mail.outbox))
