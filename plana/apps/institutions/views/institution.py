"""Views directly linked to associations."""
from rest_framework import generics

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.institutions.serializers.institution import InstitutionSerializer
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)


class AssociationInstitutionList(generics.ListAPIView):
    """Lists all institutions."""

    serializer_class = InstitutionSerializer

    def get_queryset(self):
        """GET : Lists all institutions."""
        return Institution.objects.all().order_by("name")


class AssociationInstitutionComponentList(generics.ListAPIView):
    """Lists all institution components."""

    serializer_class = InstitutionComponentSerializer

    def get_queryset(self):
        """GET : Lists all institution components."""
        return InstitutionComponent.objects.all().order_by("name")
