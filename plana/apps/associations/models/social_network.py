"""
Models describing social networks used by associations (Facebook, Twitter, Mastodon, ...).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class SocialNetwork(models.Model):
    """
    Main model.
    """

    type = models.CharField(_("Type"), max_length=32, blank=False)
    location = models.URLField(_("Location"), max_length=200, blank=False)
    association = models.ForeignKey(
        "Association",
        verbose_name=_("Association"),
        related_name="social_networks",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.type} : {self.location}"

    class Meta:
        verbose_name = _("Social network")
        verbose_name_plural = _("Social networks")
