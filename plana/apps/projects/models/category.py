"""Models describing categories (Culture, Environnement, Santé, ...)."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
