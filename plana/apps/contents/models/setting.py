"""Models describing editable settings by superadmin."""

from os.path import dirname, join

from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.libs.validators import JsonSchemaValidator


class Setting(models.Model):
    """Main model."""

    setting = models.CharField(_("Setting name"), max_length=128, unique=True)
    parameters = models.JSONField(
        _("Setting configuration"),
        blank=False,
        default=dict,
        validators=[JsonSchemaValidator(join(dirname(__file__), "schemas", "setting.json"))],
    )

    @classmethod
    def get_setting(cls, name: str):
        """Get setting."""
        try:
            return cls.objects.get(setting__iexact=name).parameters["value"]
        except (cls.DoesNotExist, KeyError) as e:
            raise Exception(
                _("General setting '%s' is missing or incorrect. Please check your settings.") % name
            ) from e

    def __str__(self) -> str:
        return str(self.setting)

    class Meta:
        verbose_name = _("General setting")
        verbose_name_plural = _("General settings")
        ordering = [
            "setting",
        ]
