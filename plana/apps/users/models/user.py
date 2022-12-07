from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

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

    # TODO Renommer les groupes et fixtures (impossible de récupérer les modèles à partir de ce point).
    _groups = {
        "Gestionnaire SVU": "svu_manager",
        "Gestionnaire Crous": "crous_manager",
        "Membre de Commission FSDIE/IdEx": "fsdie_idex_member",
        "Membre de Commission Culture-ActionS": "culture_actions_member",
        "Étudiante ou Étudiant": "student",
    }

    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("First name"), max_length=150, blank=False)
    last_name = models.CharField(_("Last name"), max_length=150, blank=False)
    phone = models.CharField(_("Phone"), max_length=32, default="", null=True)
    is_validated_by_admin = models.BooleanField(
        _("Is validated by administrator"), default=False
    )
    # TODO : Pourquoi y'a ce champ pour les assos et pas pour le GDPR ???
    association_members = models.ManyToManyField(
        Association, verbose_name=_("Associations"), through="AssociationUsers"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def has_groups(self, *groups):
        """
        :param groups: group names to check
        - return True if User belongs to one of the groups, else False
        """
        return self.groups.filter(name__in=groups).exists()

    def authorized_groups(self):
        user_filter = {"user__id": self.pk}
        return Group.objects.filter(**user_filter)

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


# Dynamically create cached properties to check the user's presence in a group
# Based on https://bugs.python.org/issue38517
for code, name in User._groups.items():

    @cached_property
    def is_in_group(self, code=code):
        return self.has_groups(code)

    attr_name = f"is_{name}"
    setattr(User, attr_name, is_in_group)
    is_in_group.__set_name__(User, attr_name)
