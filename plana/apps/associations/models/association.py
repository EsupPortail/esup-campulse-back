"""
Models describing associations and most of its details.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Association(models.Model):
    """
    Main model.
    """

    name = models.CharField(
        _("Name"), max_length=250, null=False, blank=False, unique=True
    )
    acronym = models.CharField(_("Acronym"), default="", max_length=30)
    path_logo = models.ImageField(
        _("Logo path"), blank=True
    )  # By default images are stored in MEDIA_ROOT
    alt_logo = models.TextField(_("Description"), default="")
    description = models.TextField(_("Description"), default="")
    activities = models.TextField(_("Activities"), default="")
    address = models.TextField(_("Address"), default="")
    phone = models.CharField(_("Phone"), default="", max_length=32)
    email = models.CharField(_("Email"), default="", max_length=256)
    siret = models.IntegerField(_("SIRET"), default=0)
    website = models.URLField(_("Website"), default="", max_length=200)
    student_count = models.IntegerField(_("Student count"), default=0)
    president_names = models.CharField(_("President names"), default="", max_length=256)
    is_enabled = models.BooleanField(_("Is enabled"), default=False)
    is_public = models.BooleanField(_("Is public"), default=False)
    is_site = models.BooleanField(_("Is site"), default=False)
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    approval_date = models.DateTimeField(
        _("Approval date"), null=True
    )  # date d'agrément
    last_goa_date = models.DateTimeField(
        _("Last GOA date"), null=True
    )  # date de dernière AGO
    cga_date = models.DateTimeField(_("CGA date"), null=True)  # date d'AG constitutive
    institution = models.ForeignKey(
        "Institution",
        verbose_name=_("Institution"),
        related_name="associations",
        on_delete=models.RESTRICT,
        null=True,
    )
    institution_component = models.ForeignKey(
        "InstitutionComponent",
        verbose_name=_("Institution component"),
        related_name="associations",
        on_delete=models.RESTRICT,
        null=True,
    )
    activity_field = models.ForeignKey(
        "ActivityField",
        verbose_name=_("Activity field"),
        on_delete=models.RESTRICT,
        null=True,
    )

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")


class SpaceRemovedValue(models.Transform):
    """
    Custom lookup function to compare two strings with or without spaces on a queryset.
    Thanks StackOverflow https://stackoverflow.com/a/30375271
    """

    lookup_name = 'nospaces'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "REPLACE(%s, ' ', '')" % lhs, params


models.CharField.register_lookup(SpaceRemovedValue)
