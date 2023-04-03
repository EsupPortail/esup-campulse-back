from django.db import models
from django.utils.translation import gettext_lazy as _


class Content(models.Model):
    """
    Site contents templates with HTML content
    """

    code = models.CharField(
        _("Code"), max_length=128, blank=False, null=False, unique=True
    )
    label = models.CharField(
        _("Label"), max_length=128, blank=False, null=False, unique=True
    )
    body = models.TextField(_("Body"), blank=False, null=False)

    def __str__(self):
        return f"{self.code} : {self.label}"
