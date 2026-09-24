"""Managers and QuerySet for associations."""

from django.db import models


class AssociationQueryset(models.QuerySet):

    def managed_by_user(self, user):
        """
        Returns a list of associations managed by the given user based on its linked institutions.
        user : User Object
        """
        # TODO : add better distinction on role (currently only managers have linked institutions)
        return self.filter(institution__groupinstitutionfunduser__user=user)
