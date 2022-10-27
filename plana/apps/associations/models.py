from django.db import models

class Association(models.Model):
    """
    Main table which represents an association.
    """
    username = models.CharField(default="", max_length=250, blank=False, unique=True)
    name = models.CharField(default="", max_length=250, blank=False)
    acronym = models.CharField(default="", max_length=30)
    path_logo = models.CharField(default="", max_length=250)
    description = models.TextField(default="")
    activities = models.TextField(default="")
    address = models.TextField(default="")
    phone = models.CharField(default="", max_length=25)
    email = models.CharField(default="", max_length=256)
    siret = models.IntegerField(default=0)
    website = models.CharField(default="", max_length=200)
    student_amount = models.IntegerField(default=0)
    is_enabled = models.BooleanField(default=False)
    is_site = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True) # date d'agrément
    last_goa_date = models.DateTimeField(null=True) # date de dernière AGO
    cga_date = models.DateTimeField(null=True) # date d'AG constitutive
    institution = models.ForeignKey('Institution', on_delete=models.RESTRICT)
    institution_component = models.ForeignKey('InstitutionComponent', on_delete=models.RESTRICT)
    activity_field = models.ForeignKey('ActivityField', on_delete=models.RESTRICT)

class SocialNetwork(models.Model):
    """
    Social networks from associations.
    """
    type = models.CharField(max_length=32, blank=False)
    location = models.CharField(max_length=200, blank=False)
    association = models.ForeignKey('Association', on_delete=models.CASCADE)

class Institution(models.Model):
    """
    Associations are attached to institutions.
    """
    name = models.CharField(max_length=250, blank=False)
    acronym = models.CharField(max_length=30, blank=False)

class InstitutionComponent(models.Model):
    """
    Associations are attached to components.
    """
    name = models.CharField(max_length=250, blank=False)

class ActivityField(models.Model):
    """
    Associations have an activity field.
    """
    name = models.CharField(max_length=250, blank=False)

