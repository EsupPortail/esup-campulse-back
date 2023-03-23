"""Views linked to institution components."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)


class InstitutionComponentList(generics.ListAPIView):
    """/institutions/institution_components route"""

    permission_classes = [AllowAny]
    queryset = InstitutionComponent.objects.all().order_by("name")
    serializer_class = InstitutionComponentSerializer

    def get(self, request, *args, **kwargs):
        """Lists all institution components."""
        return self.list(request, *args, **kwargs)
