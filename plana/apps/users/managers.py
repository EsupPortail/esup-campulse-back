"""Managers for User models"""

from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Q

from plana.apps.contents.models import Setting
from plana.apps.users.provider import CASProvider


class UserQuerySet(models.QuerySet):

    def managed_users(self, user):
        """Restricts a Manager User to its accessible perimeter to manage other Users"""

        # No restrictions
        if user.is_superuser or user.has_perm("users.view_user_anyone"):
            return self.all()

        if not user.is_staff:
            return self.none()

        filters = Q()
        managed_institution_acronyms = user.get_user_managed_institutions().values_list("acronym", flat=True)

        if managed_institution_acronyms.exists():
            # For manager with institutions get Users from associations of its managed institutions
            filters |= Q(associations__institution__acronym__in=managed_institution_acronyms)
            # And Fund members from funds of its managed institutions
            filters |= Q(
                groupinstitutionfunduser__fund__isnull=False,
                groupinstitutionfunduser__fund__institution__acronym__in=managed_institution_acronyms
            )

            # Also retrieve CAS users for manager with institutions if authorized
            if Setting.get_setting("CAS_INSTITUTION_ACRONYM") in managed_institution_acronyms:
                filters |= Q(socialaccount__provider=CASProvider.id)

        # Retrieve student misc users if manager misc
        if user.has_perm("users.view_user_misc"):
            filters |= Q(groupinstitutionfunduser__group__name="STUDENT_MISC")

        # A staff User cannot access to another staff User data
        # Only Users with verified email address are considered active for classic managers users
        restricted_scope = filters & Q(is_staff=False) & Q(emailaddress__verified=True)

        # Can always get yourself even with the restricted scope
        return self.filter(restricted_scope | Q(pk=user.pk)).distinct()


class CustomUserManager(UserManager):

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def managed_users(self, user):
        return self.get_queryset().managed_users(user)
