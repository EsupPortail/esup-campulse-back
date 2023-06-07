"""Views linked to commissions funds."""
from rest_framework import generics
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

    # TODO : add restriction to not create same link twice


class CommissionFundDestroy(generics.DestroyAPIView):
    """Used to destroy links between commissions and funds"""

    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
