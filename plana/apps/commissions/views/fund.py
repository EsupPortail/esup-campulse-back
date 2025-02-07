"""Views directly linked to commissions."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.serializers.fund import FundSerializer


@extend_schema(
    tags=["commissions/funds"]
)
class FundList(generics.ListAPIView):
    """/commissions/funds/names route."""

    permission_classes = [AllowAny]
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    filterset_fields = ['acronym']
