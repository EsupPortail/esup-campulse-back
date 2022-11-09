from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from allauth.socialaccount.models import SocialAccount

from plana.apps.associations.models import Association
from plana.apps.users.provider import CASProvider

class User(AbstractUser):
    """
    Extending the abstract User class.
    Following fields from Django User class are used :
        - username
        - password
        - email
        - first_name
        - last_name
        - is_active
    """
    phone = models.CharField(_("Phone"), default="", max_length=25)
    is_validated_by_admin = models.BooleanField(_("Is validated by administrator"), default=False)
    # TODO token_reset_date_user = models.DateField(default=None)
    association_members = models.ManyToManyField(
        Association, verbose_name=_("Associations"), through="AssociationUsers"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_cas_user(self):
        try:
            self.socialaccount_set.get(provider=CASProvider.id)
            return True
        except SocialAccount.DoesNotExist:
            return False

    def get_cas_user(self):
        try:
            account = self.socialaccount_set.get(provider=CASProvider.id)
            return account
        except SocialAccount.DoesNotExist:
            return None

    class Meta:
        default_permissions = []
        verbose_name = _("User")
        verbose_name_plural = _("Users")

class AssociationUsers(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    association = models.ForeignKey(Association, verbose_name=_("Association"), on_delete=models.CASCADE)
    has_office_status = models.BooleanField(_("Has office status"), default=False)

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
