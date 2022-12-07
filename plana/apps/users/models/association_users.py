from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import User


class AssociationUsers(models.Model):
    """
    Model that lists links between associations and users (which user is in which association, is the user in the association office).
    """

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    association = models.ForeignKey(
        Association, verbose_name=_("Association"), on_delete=models.CASCADE
    )
    role_name = models.CharField(_("Role name"), max_length=150, default="", null=True)
    has_office_status = models.BooleanField(_("Has office status"), default=False)
    is_president = models.BooleanField(_("Is president"), default=False)

    def __str__(self):
        return f"{self.user}, {self.association}, office : {self.has_office_status}"

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
