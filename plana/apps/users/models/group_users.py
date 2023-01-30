"""
Models describing links between GDPR consents and users
(which user has given which consent and when).
"""
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import User


class GroupUsers(models.Model):
    """
    Main model.
    """

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user}, {self.group}, {self.institution}"

    class Meta:
        verbose_name = _("User Groups")
        verbose_name_plural = _("Users Groups")

