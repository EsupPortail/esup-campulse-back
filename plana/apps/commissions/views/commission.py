"""Views directly linked to commissions."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission import Fund
from plana.apps.commissions.serializers.commission import CommissionSerializer


class CommissionList(generics.ListAPIView):
    """/commissions/ route"""

    permission_classes = [AllowAny]
    queryset = Fund.objects.all()
    serializer_class = CommissionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "acronym",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Commission acronym.",
            )
        ],
        responses={
            status.HTTP_200_OK: CommissionSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all commission types."""
        acronym = request.query_params.get("acronym")

        if acronym is not None and acronym != "":
            self.queryset = self.queryset.filter(acronym=acronym)

        return self.list(request, *args, **kwargs)
