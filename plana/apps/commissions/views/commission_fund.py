"""Views linked to commissions funds."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.serializers.commission_fund import CommissionFundSerializer


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
            status.HTTP_200_OK: CommissionFundSerializer,
        },
        tags=["commissions/funds"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all links between commissions and funds."""
        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: CommissionFundSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["commissions/funds"],
    )
    def post(self, request, *args, **kwargs):
        """Creates a link between a commission and a fund."""
        try:
            Commission.objects.get(id=request.data["commission"])
            Fund.objects.get(id=request.data["fund"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission or fund does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission_funds_count = CommissionFund.objects.filter(
            commission_id=request.data["commission"],
            fund_id=request.data["fund"],
        ).count()
        if commission_funds_count > 0:
            return response.Response(
                {"error": _("This commission is already linked to this fund.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class CommissionFundRetrieve(generics.RetrieveAPIView):
    """/commissions/{commission_id}/funds route"""

    permission_classes = [AllowAny]
    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: CommissionFundSerializer,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["commissions/funds"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieves all funds linked to a commission."""
        try:
            Commission.objects.get(id=kwargs["commission_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(
            self.queryset.filter(commission_id=kwargs["commission_id"]), many=True
        )
        return response.Response(serializer.data)


class CommissionFundDestroy(generics.DestroyAPIView):
    """/commissions/{commission_id}/funds/{fund_id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: CommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["commissions/funds"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a link between commission and fund."""
        try:
            Commission.objects.get(id=kwargs["commission_id"])
            commission_fund = CommissionFund.objects.get(
                commission_id=kwargs["commission_id"], fund_id=kwargs["fund_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Link between commission and fund does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        commission_fund.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
