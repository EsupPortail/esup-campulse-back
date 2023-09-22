"""Views linked to institution components."""
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)


class InstitutionComponentList(generics.ListAPIView):
    """/institutions/institution_components route."""

    permission_classes = [AllowAny]
    queryset = InstitutionComponent.objects.all().order_by("name")
    serializer_class = InstitutionComponentSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: InstitutionComponentSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """List all institution components."""
        return self.list(request, *args, **kwargs)
