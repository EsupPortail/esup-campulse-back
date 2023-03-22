"""Views linked to institution components."""
from rest_framework import generics

from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)


class InstitutionComponentList(generics.ListAPIView):
    """Lists all institution components."""

    serializer_class = InstitutionComponentSerializer

    def get_queryset(self):
        """GET : Lists all institution components."""
        return InstitutionComponent.objects.all().order_by("name")
