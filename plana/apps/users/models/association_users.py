"""
Models describing links between associations and users
(which user is in which association, is the user in the association office, ...).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import User


class AssociationUsers(models.Model):
    """
    Main model.
    """

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
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
