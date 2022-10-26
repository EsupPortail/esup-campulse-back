from django.db import models

class Association(models.Model):
    """
    Main table which represents an association.
    """
    username_association = models.CharField(default="", max_length=250, blank=False, unique=True)
    name_association = models.CharField(default="", max_length=250, blank=False)
    acronym_association = models.CharField(default="", max_length=30)
    path_logo_association = models.CharField(default="", max_length=250)
    description_association = models.TextField(default="")
    activities_association = models.TextField(default="")
    address_association = models.TextField(default="")
    phone_association = models.CharField(default="", max_length=25)
    email_association = models.CharField(default="", max_length=256)
    siret_association = models.IntegerField(default=0)
    website_association = models.CharField(default="", max_length=200)
    student_amount_association = models.IntegerField(default=0)
    is_enabled_association = models.BooleanField(default=False)
    is_site_association = models.BooleanField(default=False)
    created_date_association = models.DateTimeField(auto_now_add=True)
    approval_date_association = models.DateTimeField(null=True) # date d'agrément
    last_goa_date_association = models.DateTimeField(null=True) # date de dernière AGO
    cga_date_association = models.DateTimeField(null=True) # date d'AG constitutive
    institution = models.ForeignKey('Institution', on_delete=models.RESTRICT)
    institution_component = models.ForeignKey('InstitutionComponent', on_delete=models.RESTRICT)
    activity_field = models.ForeignKey('ActivityField', on_delete=models.RESTRICT)

class SocialNetwork(models.Model):
    """
    Social networks from associations.
    """
    type_social_network = models.CharField(max_length=32, blank=False)
    location_social_network = models.CharField(max_length=200, blank=False)
    association = models.ForeignKey('Association', on_delete=models.CASCADE)

class Institution(models.Model):
    """
    Associations are attached to institutions.
    """
    name_institution = models.CharField(max_length=250, blank=False)
    acronym_institution = models.CharField(max_length=30, blank=False)

class InstitutionComponent(models.Model):
    """
    Associations are attached to components.
    """
    name_institution_component = models.CharField(max_length=250, blank=False)

class ActivityField(models.Model):
    """
    Associations have an activity field.
    """
    name_activity_field = models.CharField(max_length=250, blank=False)

