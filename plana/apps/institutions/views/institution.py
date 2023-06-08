"""Views directly linked to institutions."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.serializers.institution import InstitutionSerializer


class InstitutionList(generics.ListAPIView):
    """/institutions/ route"""

    permission_classes = [AllowAny]
    queryset = Institution.objects.all().order_by("name")
    serializer_class = InstitutionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "acronym",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Institution acronym.",
            )
        ],
        responses={
            status.HTTP_200_OK: InstitutionSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all institutions."""
        acronym = request.query_params.get("acronym")

        if acronym is not None and acronym != "":
            self.queryset = self.queryset.filter(acronym=acronym)

        return self.list(request, *args, **kwargs)
