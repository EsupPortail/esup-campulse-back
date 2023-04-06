"""Views directly linked to commissions."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.serializers.commission import CommissionSerializer


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "acronym",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Commission acronym.",
            )
        ]
    )
)
class CommissionList(generics.ListAPIView):
    """/commissions/ route"""

    permission_classes = [AllowAny]
    serializer_class = CommissionSerializer

    def get_queryset(self):
        queryset = Commission.objects.all()
        acronym = self.request.query_params.get("acronym")
        if acronym is not None and acronym != "":
            queryset = queryset.filter(acronym=acronym)
        return queryset

    def get(self, request, *args, **kwargs):
        """Lists all commission types."""
        return self.list(request, *args, **kwargs)
