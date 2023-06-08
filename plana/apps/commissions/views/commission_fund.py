"""Views linked to commissions funds."""
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.serializers.commission_fund import CommissionFundSerializer


class CommissionFundListCreate(generics.ListCreateAPIView):
    """Used to list and create links between commissions and funds"""

    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def post(self, request, *args, **kwargs):
        """Creates a link between a commission and a fund."""
        commission_funds = CommissionFund.objects.filter(
            commission_id=request.data["commission"],
            fund_id=request.data["fund"],
        ).count()
        if commission_funds > 0:
            return response.Response(
                {"error": _("This commission is already linked to this fund.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class CommissionFundDestroy(generics.DestroyAPIView):
    """Used to destroy links between commissions and funds"""

    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
