from django.db import models
from django.utils.translation import gettext as _


class Association(models.Model):
    """
    Main table which represents an association.
    """
    name = models.CharField(_("Name"), default="", max_length=250, null=False, blank=False, unique=True)
    acronym = models.CharField(_("Acronym"), default="", max_length=30)
    path_logo = models.CharField(_("Logo path"), default="", max_length=250)
    description = models.TextField(_("Description"), default="")
    activities = models.TextField(_("Activities"), default="")
    address = models.TextField(_("Address"), default="")
    phone = models.CharField(_("Phone"), default="", max_length=25)
    email = models.CharField(_("Email"), default="", max_length=256)
    siret = models.IntegerField(_("SIRET"), default=0)
    website = models.URLField(_("Website"), default="", max_length=200)
    student_count = models.IntegerField(_("Student count"), default=0)
    is_enabled = models.BooleanField(_("Is active"), default=False)
    is_site = models.BooleanField(_("Is site"), default=False)
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    approval_date = models.DateTimeField(_("Approval date"), null=True) # date d'agrément
    last_goa_date = models.DateTimeField(_("Last GOA date"), null=True) # date de dernière AGO
    cga_date = models.DateTimeField(_("CGA date"), null=True) # date d'AG constitutive
    institution = models.ForeignKey(
        'Institution', verbose_name=_("Institution"), related_name='associations', on_delete=models.RESTRICT
    )
    institution_component = models.ForeignKey(
        'InstitutionComponent', verbose_name=_("Institution component"), related_name='associations',
        on_delete=models.RESTRICT
    )
    activity_field = models.ForeignKey('ActivityField', verbose_name=_("Activity field"), on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")


class SocialNetwork(models.Model):
    """
    Social networks from associations.
    """
    type = models.CharField(_("Type"), max_length=32, blank=False)
    location = models.URLField(_("Location"), max_length=200, blank=False)
    association = models.ForeignKey(
        'Association', verbose_name=_("Association"), related_name='social_networks', on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.type} : {self.location}"

    class Meta:
        verbose_name = _("Social network")
        verbose_name_plural = _("Social networks")


class Institution(models.Model):
    """
    Associations are attached to institutions.
    """
    name = models.CharField(_("Name"), max_length=250, blank=False)
    acronym = models.CharField(_("Acronym"), max_length=30, blank=False)

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")


class InstitutionComponent(models.Model):
    """
    Associations are attached to components.
    """
    name = models.CharField(_("Name"), max_length=250, blank=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Institution component")
        verbose_name_plural = _("Institution components")


class ActivityField(models.Model):
    """
    Associations have an activity field.
    """
    name = models.CharField(_("Name"), max_length=250, blank=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Activity field")
        verbose_name_plural = _("Activity fields")
