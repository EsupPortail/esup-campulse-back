"""
Models describing associations and most of its details.
"""
import datetime
import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.storages import DynamicThumbnailImageField
from plana.apps.institutions.models import Institution, InstitutionComponent


def get_logo_path(instance, filename):
    file_basename, extension = os.path.splitext(filename)
    year = datetime.datetime.now().strftime('%Y')
    return (
        os.path.join(
            settings.S3_LOGO_FILEPATH if hasattr(settings, 'S3_LOGO_FILEPATH') else '',
            year,
            f'{file_basename}{extension}',
        )
        .lower()
        .replace(' ', '_')
    )


class Association(models.Model):
    """
    Main model.
    """

    name = models.CharField(
        _("Name"), max_length=250, null=False, blank=False, unique=True
    )
    acronym = models.CharField(_("Acronym"), default="", max_length=30)
    path_logo = DynamicThumbnailImageField(
        _("Dynamic thumbnails for the logo"),
        null=True,
        blank=True,
        resize_source_to="base",
        pregenerated_sizes=["list", "detail"],
        upload_to=get_logo_path,
    )  # By default images are stored in MEDIA_ROOT
    alt_logo = models.TextField(
        _("Logo description"), default="", null=True, blank=True
    )
    description = models.TextField(_("Description"), default="")
    activities = models.TextField(_("Activities"), default="")
    address = models.TextField(_("Address"), default="")
    phone = models.CharField(_("Phone"), default="", max_length=32)
    email = models.CharField(_("Email"), default="", max_length=256)
    siret = models.CharField(_("SIRET"), default="", max_length=14)
    website = models.URLField(_("Website"), default="", max_length=200)
    student_count = models.IntegerField(_("Student count"), default=0)
    president_names = models.CharField(_("President names"), default="", max_length=256)
    president_phone = models.CharField(_("President Phone"), default="", max_length=32)
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
    social_networks = models.JSONField(
        default=list
    )  # JSON format : [{"type": "sn_name", "location": "sn_url"}]
    institution = models.ForeignKey(
        Institution,
        verbose_name=_("Institution"),
        related_name="associations",
        on_delete=models.RESTRICT,
        null=True,
    )
    institution_component = models.ForeignKey(
        InstitutionComponent,
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
        permissions = [
            ("add_association_same_institution", "Can create an association from the same institution."),
            ("add_association_any_institution", "Can create an association from any institution."),
            ("change_association_same_institution", "Can change most fields of an association from the same institution."),
            ("change_association_any_institution", "Can change fields for an association from any institution."),
            ("change_association_any_president", "Can change fields for an association from any president."),
            ("change_association_all_fields", "Can change institution_id, is_enabled, is_public, is_site for an association."),
            ("delete_association_same_institution", "Can delete an association from the same institution."),
            ("delete_association_any_institution", "Can delete an association from any institution."),
            ("view_association_not_enabled", "Can view a not enabled association."),
            ("view_association_not_public", "Can view a not public association."),
        ]


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
