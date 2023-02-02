"""
Models describing users and most of its details.
"""
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.consents.models.consent import GDPRConsent
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.provider import CASProvider


class AssociationUsers(models.Model):
    """
    Main model.
    """

    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    association = models.ForeignKey(
        Association, verbose_name=_("Association"), on_delete=models.CASCADE
    )
    role_name = models.CharField(_("Role name"), max_length=150, default="", null=True)
    is_president = models.BooleanField(_("Is president"), default=False)
    can_be_president = models.BooleanField(_("Can be president"), default=False)

    def __str__(self):
        return f"{self.user}, {self.association}, office : {self.can_be_president}"

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
        permissions = []


class GroupInstitutionUsers(models.Model):
    """
    Main model.
    """

    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True)
    is_staff = models.BooleanField(_("Is staff"), default=False)

    def __str__(self):
        return f"{self.user}, {self.group}, {self.institution}"

    class Meta:
        verbose_name = _("User Institution Groups")
        verbose_name_plural = _("Users Institution Groups")
        permissions = []


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
    associations = models.ManyToManyField(
        Association, verbose_name=_("Associations"), through="AssociationUsers"
    )
    consents_given = models.ManyToManyField(
        GDPRConsent, verbose_name=_("GDPR Consents"), through="GDPRConsentUsers"
    )
    groups_institutions = models.ManyToManyField(
        Group,
        verbose_name=_("Groups"),
        through="GroupInstitutionUsers",
        related_name="group_institution_set",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        """
        Overriden has_perm to check for institutions.
        """
        if self.is_superuser:
            return True
        else:
            groups_institutions_user = GroupInstitutionUsers.objects.filter(
                user_id=self.pk
            )
            for group_institution_user in groups_institutions_user:
                group_user = Group.objects.get(id=group_institution_user.group_id)
                for permission in group_user.permissions.all():
                    if (
                        perm
                        == f"{permission.content_type.app_label}.{permission.codename}"
                    ):
                        return True
            return False

    def is_cas_user(self):
        """
        Returns True if the user account was generated through CAS on signup
        (checks if a related row is in socialaccount table).
        """

        try:
            self.socialaccount_set.get(provider=CASProvider.id)
            return True
        except SocialAccount.DoesNotExist:
            return False

    def is_in_institution(self, institution_id):
        """
        Checks if a user is linked to an institution.
        """

        try:
            GroupInstitutionUsers.objects.get(
                user_id=self.pk, institution_id=institution_id
            )
            return True
        except ObjectDoesNotExist:
            return False

    def is_staff_in_institution(self, institution_id):
        """
        Checks if a user is linked as manager to an institution.
        """

        try:
            GroupInstitutionUsers.objects.get(
                user_id=self.pk, institution_id=institution_id, is_staff=True
            )
            return True
        except ObjectDoesNotExist:
            return False

    def is_staff(self):
        """
        Checks if a user is linked as manager to an institution.
        """

        try:
            GroupInstitutionUsers.objects.get(user_id=self.pk, is_staff=True)
            return True
        except ObjectDoesNotExist:
            return False

    def is_in_association(self, association_id):
        """
        Checks if a user can read an association.
        """

        try:
            AssociationUsers.objects.get(user_id=self.pk, association_id=association_id)
            return True
        except ObjectDoesNotExist:
            return False

    def is_president_in_association(self, association_id):
        """
        Checks if a user can write in an association.
        """

        try:
            AssociationUsers.objects.filter(
                models.Q(is_president=True) | models.Q(can_be_president=True)
            ).get(user_id=self.pk, association_id=association_id)
            return True
        except ObjectDoesNotExist:
            return False

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [
            ("change_user_anyone", "Can change all users."),
            ("view_user_anyone", "Can view all users."),
        ]
