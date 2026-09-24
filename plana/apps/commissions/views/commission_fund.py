"""Views linked to commissions funds."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.commissions.serializers.commission_fund import CommissionFundSerializer


@extend_schema(tags=["commissions/funds"])
class CommissionFundListCreate(generics.ListCreateAPIView):
    """/commissions/funds route"""

    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()


@extend_schema(tags=["commissions/funds"])
class CommissionFundRetrieve(generics.ListAPIView):
    """/commissions/{commission_id}/funds route."""

    permission_classes = [AllowAny]
    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    def get_queryset(self):
        return self.queryset.filter(commission_id=self.kwargs["commission_id"])


@extend_schema(tags=["commissions/funds"])
class CommissionFundDestroy(generics.DestroyAPIView):
    """/commissions/{commission_id}/funds/{fund_id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            commission_id=self.kwargs["commission_id"],
            fund_id=self.kwargs["fund_id"])
