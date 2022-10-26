from django.db import models
from django.contrib.auth.models import AbstractUser


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
    is_cas_user = models.BooleanField(default=False)
    # TODO token_reset_date_user = models.DateField(default=None)

    class Meta:
        default_permissions = []

