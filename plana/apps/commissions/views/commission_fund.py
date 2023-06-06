"""Views linked to commissions funds."""
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.serializers.commission_fund import CommissionFundSerializer


class CommissionFundListCreate(generics.ListCreateAPIView):
    queryset = CommissionFund.objects.all()
    serializer_class = CommissionFundSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()
