"""
Views directly linked to associations.
"""
from django.utils.translation import gettext_lazy as _
from rest_framework import generics

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.institutions.serializers.institution import InstitutionSerializer
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)


class AssociationInstitutionComponentList(generics.ListAPIView):
    """
    GET : Lists all institution components.
    """

    serializer_class = InstitutionComponentSerializer

    def get_queryset(self):
        return InstitutionComponent.objects.all().order_by("name")


class AssociationInstitutionList(generics.ListAPIView):
    """
    GET : Lists all institutions.
    """

    serializer_class = InstitutionSerializer

    def get_queryset(self):
        return Institution.objects.all().order_by("name")
