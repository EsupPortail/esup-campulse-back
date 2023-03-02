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
