from django.db import models
from django.utils.translation import gettext_lazy as _


class InstitutionComponent(models.Model):
    """
    Associations are attached to components (faculté de médecine, IUT, ...).
    """

    name = models.CharField(_("Name"), max_length=250, blank=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Institution component")
        verbose_name_plural = _("Institution components")
