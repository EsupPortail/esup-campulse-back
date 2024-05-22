"""Models describing users and most of its details."""

import datetime

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.models.fund import Fund
from plana.apps.contents.models.setting import Setting
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.users.provider import CASProvider


class AssociationUser(models.Model):
    """Model that defines the link between a user and an association."""

    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    association = models.ForeignKey(Association, verbose_name=_("Association"), on_delete=models.CASCADE)
    is_president = models.BooleanField(_("Is president"), default=False)
    can_be_president_from = models.DateField(_("Can be president from"), null=True)
    can_be_president_to = models.DateField(_("Can be president to"), null=True)
    is_validated_by_admin = models.BooleanField(_("Is validated by admin"), default=False)
    is_vice_president = models.BooleanField(_("Is vice president"), default=False)
    is_secretary = models.BooleanField(_("Is secretary"), default=False)
    is_treasurer = models.BooleanField(_("Is treasurer"), default=False)

    def __str__(self):
        return f"{self.user} - {self.association}"

    class Meta:
        verbose_name = _("User Association")
        verbose_name_plural = _("Users Associations")
        permissions = [
            (
                "change_associationuser_any_institution",
                "Can change associations for all users.",
            ),
            (
                "delete_associationuser_any_institution",
                "Can delete associations for all users.",
            ),
            ("view_associationuser_anyone", "Can view all associations for a user."),
        ]


class GroupInstitutionFundUser(models.Model):
    """
    Define the link between a user and a group.

    And an institution if user is a manager.
    And a fund if user is a fund member.
    """

    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    institution = models.ForeignKey(Institution, on_delete=models.RESTRICT, null=True)
    fund = models.ForeignKey(Fund, on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return f"{self.user} - {self.group} - {self.institution} - {self.fund}"

    class Meta:
        verbose_name = _("User Institution Fund Groups")
        verbose_name_plural = _("Users Institution Fund Groups")
        permissions = [
            (
                "add_groupinstitutionfunduser_any_group",
                "Can add restricted groups to a user.",
            ),
            (
                "delete_groupinstitutionfunduser_any_group",
                "Can delete restricted groups to a user.",
            ),
            (
                "view_groupinstitutionfunduser_any_group",
                "Can view all groups for a user.",
            ),
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
    address = models.TextField(_("Address"), default="")
    zipcode = models.CharField(_("Zipcode"), max_length=32, default="")
    city = models.CharField(_("City"), max_length=128, default="")
    country = models.CharField(_("Country"), max_length=128, default="")
    phone = models.CharField(_("Phone"), default="", max_length=32, null=True)
    can_submit_projects = models.BooleanField(_("Can submit projects"), default=True)
    password_last_change_date = models.DateField(_("Password last change date"), null=True)
    is_validated_by_admin = models.BooleanField(_("Is validated by administrator"), default=False)
    is_student = models.BooleanField(_("Is student"), default=False)
    associations = models.ManyToManyField(Association, verbose_name=_("Associations"), through="AssociationUser")
    groups_institutions_funds = models.ManyToManyField(
        Group,
        verbose_name=_("Groups"),
        through="GroupInstitutionFundUser",
        related_name="group_institution_fund_set",
    )

    def has_perm(self, perm, obj=None):
        """Overriden has_perm to check for institutions."""
        if self.is_superuser:
            return True
        return (
            Permission.objects.filter(
                group__id__in=Group.objects.filter(
                    id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("group_id")
                ).values_list("id"),
                codename=perm.split(".")[1],
            ).count()
            > 0
        )

    def can_access_project(self, project_obj):
        """Check if a user can access a project as association president, misc user, fund member, or manager."""
        if project_obj.association is not None:
            try:
                AssociationUser.objects.get(user_id=self.pk, association_id=project_obj.association)
                return True
            except ObjectDoesNotExist:
                pass

        if project_obj.user is not None:
            if project_obj.user == self:
                return True

        if self.get_user_funds().count() != 0 or self.get_user_managed_funds().count() != 0:
            user_funds_ids = self.get_user_funds().values_list("id")
            user_managed_funds_ids = self.get_user_managed_funds().values_list("id")
            project_funds_ids = CommissionFund.objects.filter(
                id__in=ProjectCommissionFund.objects.filter(project_id=project_obj.id).values_list(
                    "commission_fund_id"
                )
            ).values_list("fund_id")
            if (
                len(set(project_funds_ids).intersection(user_funds_ids)) == 0
                and len(set(project_funds_ids).intersection(user_managed_funds_ids)) == 0
                and not self.is_staff
            ):
                return False
            return True

        if self.is_staff:
            if project_obj.association_id is not None:
                institution_id = Institution.objects.get(
                    id=Association.objects.get(id=project_obj.association_id).institution_id
                )
                if institution_id not in self.get_user_managed_institutions():
                    return False
            if project_obj.user is not None and not self.has_perm("users.change_user_misc"):
                return False
            return True

        return False

    def can_edit_project(self, project_obj):
        """Check if a user can edit a project as association president, misc user, fund member, or manager."""
        if not self.can_access_project(project_obj):
            return False

        if project_obj.association_user is not None and self.get_user_funds().count() == 0 and not self.is_staff:
            member = AssociationUser.objects.get(user_id=self.pk, association_id=project_obj.association)
            if (
                not member.is_president
                and not self.is_president_in_association(project_obj.association)
                and member.id != project_obj.association_user.id
            ):
                return False
            return True

        return True

    def get_user_associations(self):
        """Return a list of Association IDs linked to a student user."""
        return Association.objects.filter(
            id__in=AssociationUser.objects.filter(user_id=self.pk).values_list("association_id")
        )

    def get_user_managed_associations(self):
        """Return a list of Association IDs linked to a manager user."""
        return Association.objects.filter(
            institution_id__in=Institution.objects.filter(
                id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("institution_id")
            ).values_list("id")
        )

    def get_user_funds(self):
        """Return a list of Fund IDs linked to a student user."""
        return Fund.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("fund_id")
        )

    def get_user_managed_funds(self):
        """Return a list of Fund IDs linked to a manager user."""
        return Fund.objects.filter(
            institution_id__in=Institution.objects.filter(
                id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("institution_id")
            ).values_list("id")
        )

    def get_user_groups(self):
        """Return a list of Group IDs linked to a user."""
        return Group.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("group_id")
        )

    def get_user_institutions(self):
        """Return a list of Institution IDs linked to a student user."""
        return Institution.objects.filter(
            models.Q(
                id__in=Association.objects.filter(
                    id__in=AssociationUser.objects.filter(user_id=self.pk).values_list("association_id")
                ).values_list("institution_id")
            )
            | models.Q(
                id__in=Fund.objects.filter(
                    id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("fund_id")
                ).values_list("institution_id")
            )
        )

    def get_user_managed_institutions(self):
        """Return a list of Institution IDs linked to a manager user."""
        return Institution.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(user_id=self.pk).values_list("institution_id")
        )

    def get_user_default_manager_emails(self):
        """Return a list of manager email addresses affected to a user."""
        assos_user = AssociationUser.objects.filter(user_id=self.pk)
        funds_user = GroupInstitutionFundUser.objects.filter(user_id=self.pk, fund_id__isnull=False)
        institutions_user = GroupInstitutionFundUser.objects.filter(user_id=self.pk, institution_id__isnull=False)
        managers_emails = []
        if institutions_user.count() > 0:
            for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                if user_to_check.has_perm("users.add_groupinstitutionfunduser_any_group"):
                    managers_emails.append(user_to_check.email)
        elif assos_user.count() > 0 or funds_user.count() > 0:
            for institution in self.get_user_institutions():
                managers_emails += institution.default_institution_managers().values_list("email", flat=True)
            managers_emails = list(set(managers_emails))
        elif self.is_cas_user() is True:
            institution = Institution.objects.get(acronym=Setting.get_setting("CAS_INSTITUTION_ACRONYM"))
            managers_emails += institution.default_institution_managers().values_list("email", flat=True)
            managers_emails = list(set(managers_emails))
        else:
            for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                if user_to_check.has_perm("users.change_user_misc"):
                    managers_emails.append(user_to_check.email)
        return managers_emails

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
            AssociationUser.objects.get(
                user_id=self.pk,
                association_id=association_id,
                is_validated_by_admin=True,
            )
            return True
        except ObjectDoesNotExist:
            return False

    def is_member_in_fund(self, fund_id):
        """Check if a user is linked as member to a fund."""
        return (
            GroupInstitutionFundUser.objects.filter(
                models.Q(user_id=self.pk, fund_id=fund_id)
                | models.Q(user_id=self.pk, institution_id=Fund.objects.get(id=fund_id).institution_id)
            ).count()
            > 0
        )

    def is_president_in_association(self, association_id):
        """Check if a user can write in an association."""
        try:
            now = datetime.date.today()
            AssociationUser.objects.filter(
                models.Q(is_president=True)
                | models.Q(
                    can_be_president_from__lte=now,
                    can_be_president_to__isnull=True,
                )
                | models.Q(
                    can_be_president_from__isnull=True,
                    can_be_president_to__gte=now,
                )
                | models.Q(
                    can_be_president_from__lte=now,
                    can_be_president_to__gte=now,
                )
            ).get(
                user_id=self.pk,
                association_id=association_id,
                is_validated_by_admin=True,
            )
            return True
        except ObjectDoesNotExist:
            return False

    def is_staff_for_association(self, association_id):
        """Check if a user is linked as manager for an association."""
        if self.is_staff:
            return GroupInstitutionFundUser.objects.filter(
                user_id=self.pk,
                institution_id=Association.objects.get(id=association_id).institution_id,
            )
        return False

    def is_staff_in_institution(self, institution_id):
        """Check if a user is linked as manager to an institution."""
        if self.is_staff:
            return GroupInstitutionFundUser.objects.filter(user_id=self.pk, institution_id=institution_id)
        return False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [
            ("add_user_misc", "Can add a user with no association linked."),
            ("change_user_misc", "Can change a user with no association linked."),
            ("change_user_all_fields", "Can change can_submit_projects on a user."),
            ("delete_user_misc", "Can delete a user with no association linked."),
            ("view_user_misc", "Can view a user with no association linked."),
            ("view_user_anyone", "Can view all users."),
        ]
