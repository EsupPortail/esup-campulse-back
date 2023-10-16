"""Models describing associations activity fields (culture, international, santé, sport, ...)."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ActivityField(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Activity field")
        verbose_name_plural = _("Activity fields")
