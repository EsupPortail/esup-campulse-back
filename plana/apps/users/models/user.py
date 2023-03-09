"""Models describing users and most of its details."""
import datetime

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.consents.models.consent import GDPRConsent
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.provider import CASProvider


class AssociationUsers(models.Model):
    """Model that defines the link between a user and an association."""

    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    association = models.ForeignKey(
        Association, verbose_name=_("Association"), on_delete=models.CASCADE
    )
    is_president = models.BooleanField(_("Is president"), default=False)
    can_be_president = models.BooleanField(_("Can be president"), default=False)
    can_be_president_from = models.DateField(_("Can be president from"), null=True)
    can_be_president_to = models.DateField(_("Can be president to"), null=True)
    is_validated_by_admin = models.BooleanField(
        _("Is validated by admin"), default=False
    )
    is_vice_president = models.BooleanField(_("Is vice president"), default=False)
    is_secretary = models.BooleanField(_("Is secretary"), default=False)
    is_treasurer = models.BooleanField(_("Is treasurer"), default=False)
    can_submit_projects = models.BooleanField(_("Can submit projects"), default=True)

    def __str__(self):
        return f"{self.user}, {self.association}, office : {self.can_be_president}"

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
        permissions = [
            (
                "change_associationusers_any_institution",
                "Can change associations for all users.",
            ),
            (
                "delete_associationusers_any_institution",
                "Can delete associations for all users.",
            ),
            ("view_associationusers_anyone", "Can view all associations for a user."),
        ]


class GroupInstitutionCommissionUsers(models.Model):
    """Define the link between a user, a group (and an institution if user is a manager) (and a commission if user is a commission member)."""

    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user}, {self.group}, {self.institution}, {self.commission}"

    class Meta:
        verbose_name = _("User Institution Commission Groups")
        verbose_name_plural = _("Users Institution Commission Groups")
        permissions = [
            (
                "view_groupinstitutioncommissionusers_anyone",
                "Can view all groups for a user.",
            )
        ]


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
    password_last_change_date = models.DateField(
        _("Password last change date"), null=True
    )
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
        through="GroupInstitutionCommissionUsers",
        related_name="group_institution_set",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        """Overriden has_perm to check for institutions."""
        if self.is_superuser:
            return True
        groups_institutions_user = GroupInstitutionCommissionUsers.objects.filter(
            user_id=self.pk
        )
        for group_institution_user in groups_institutions_user:
            group_user = Group.objects.get(id=group_institution_user.group_id)
            for permission in group_user.permissions.all():
                if perm == f"{permission.content_type.app_label}.{permission.codename}":
                    return True
        return False

    def get_user_associations(self):
        """Return a list of Association IDs linked to a user."""
        return Association.objects.filter(
            id__in=AssociationUsers.objects.filter(user_id=self.pk).values_list(
                "association_id"
            )
        ).values_list("id")

    def get_user_institutions(self):
        """Return a list of Institution objects linked to a user."""
        if self.is_staff:
            return Institution.objects.filter(
                id__in=GroupInstitutionCommissionUsers.objects.filter(
                    user_id=self.pk
                ).values_list("institution_id")
            )
        return Institution.objects.filter(
            id__in=Association.objects.filter(
                id__in=AssociationUsers.objects.filter(user_id=self.pk).values_list(
                    "association_id"
                )
            ).values_list("institution_id")
        )

    def has_validated_email_user(self):
        """Return True if the user account has a validated email."""
        try:
            EmailAddress.objects.get(user_id=self.pk, email=self.email, verified=True)
            return True
        except ObjectDoesNotExist:
            return False

    def is_cas_user(self):
        """Return True if the user account was generated through CAS on signup."""
        try:
            self.socialaccount_set.get(provider=CASProvider.id)
            return True
        except SocialAccount.DoesNotExist:
            return False

    def is_in_association(self, association_id):
        """Check if a user can read an association."""
        try:
            AssociationUsers.objects.get(
                user_id=self.pk,
                association_id=association_id,
                is_validated_by_admin=True,
            )
            return True
        except ObjectDoesNotExist:
            return False

    def is_president_in_association(self, association_id):
        """Check if a user can write in an association."""
        try:
            now = datetime.datetime.now()
            AssociationUsers.objects.filter(
                models.Q(is_president=True)
                | models.Q(
                    can_be_president=True,
                    can_be_president_from__gte=now,
                    can_be_president_to__lte=now,
                )
            ).get(
                user_id=self.pk,
                association_id=association_id,
                is_validated_by_admin=True,
            )
            return True
        except ObjectDoesNotExist:
            return False

    def is_staff_in_institution(self, institution_id):
        """Check if a user is linked as manager to an institution."""
        if self.is_staff:
            try:
                GroupInstitutionCommissionUsers.objects.get(
                    user_id=self.pk, institution_id=institution_id
                )
                return True
            except ObjectDoesNotExist:
                return False
        return False

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [
            ("add_user_misc", "Can add a user with no association linked."),
            ("change_user_misc", "Can change a user with no association linked."),
            ("delete_user_misc", "Can delete a user with no association linked."),
            ("view_user_misc", "Can view a user with no association linked."),
            ("view_user_anyone", "Can view all users."),
        ]
