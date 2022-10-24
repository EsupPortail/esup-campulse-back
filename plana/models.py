from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extending the abstract User class.
    """
    id_user = models.BigAutoField(primary_key=True)
