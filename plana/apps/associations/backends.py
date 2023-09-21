"""Testers for health check."""
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException

from plana.apps.associations.models.association import Association


class AssociationCheckBackend(BaseHealthCheckBackend):
    """Backend tester for health check."""

    critical_service = True

    def check_status(self):
        try:
            association_count = Association.objects.count()
        except Exception as e:
            raise HealthCheckException(e) from e
        if association_count < 1:
            raise HealthCheckException('Seems to have no Association')

    def identifier(self):
        return self.__class__.__name__
