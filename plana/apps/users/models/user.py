from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from allauth.socialaccount.models import SocialAccount

from plana.apps.associations.models.association import Association
from plana.apps.users.provider import CASProvider


class User(AbstractUser):
    """
    Model that extends the abstract User class.
    Following fields from Django User class are used :
        - username
        - password
        - email
        - first_name
        - last_name
        - is_active
    """

    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("First name"), max_length=150, blank=False)
    last_name = models.CharField(_("Last name"), max_length=150, blank=False)
    phone = models.CharField(_("Phone"), max_length=32, default="", null=True)
    is_validated_by_admin = models.BooleanField(
        _("Is validated by administrator"), default=False
    )
    # TODO token_reset_date_user = models.DateField(default=None)
    association_members = models.ManyToManyField(
        Association, verbose_name=_("Associations"), through="AssociationUsers"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_cas_user(self):
        """
        Returns True if the user account was generated through CAS on signup (checks if a related row is in socialaccount table).
        """

        try:
            self.socialaccount_set.get(provider=CASProvider.id)
            return True
        except SocialAccount.DoesNotExist:
            return False

    def get_cas_user(self):
        """
        Returns user account CAS details if it was generated through CAS on signup (from a related row in socialaccount table).
        """

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
    """
    Model that lists links between associations and users (which user is in which association, is the user in the association office).
    """

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    association = models.ForeignKey(
        Association, verbose_name=_("Association"), on_delete=models.CASCADE
    )
    has_office_status = models.BooleanField(_("Has office status"), default=False)

    def __str__(self):
        return f"{self.user}, {self.association}, office : {self.has_office_status}"

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
