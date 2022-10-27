from django.db import models
from django.contrib.auth.models import AbstractUser
from plana.apps.associations.models import Association


class User(AbstractUser):
    """
    Extending the abstract User class.
    Following fields from Django User class are used :
        - username
        - password
        - email
        - first_name
        - last_name
        - is_active
    """
    is_cas = models.BooleanField(default=False)
    # TODO token_reset_date_user = models.DateField(default=None)
    association_members = models.ManyToManyField(Association, through="AssociationUsers")

    class Meta:
        default_permissions = []

class AssociationUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    has_office_status = models.BooleanField(default=False)

