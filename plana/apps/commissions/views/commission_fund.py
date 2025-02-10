"""Views linked to commissions funds."""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.serializers.commission_fund import CommissionFundSerializer


@extend_schema(
    tags=["commissions/funds"],
)
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

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: CommissionFundSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a link between a commission and a fund."""
        try:
            Commission.objects.get(id=request.data["commission"])
            Fund.objects.get(id=request.data["fund"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission or fund does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        commission_funds = CommissionFund.objects.filter(
            commission_id=request.data["commission"],
            fund_id=request.data["fund"],
        ).exists()
        if commission_funds:
            return response.Response(
                {"error": _("This commission is already linked to this fund.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


@extend_schema(
    tags=["commissions/funds"]
)
class CommissionFundRetrieve(generics.ListAPIView):
    """/commissions/{commission_id}/funds route."""

    permission_classes = [AllowAny]
    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    def get_queryset(self):
        return self.queryset.filter(commission_id=self.kwargs["commission_id"])


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
