"""Views directly linked to commissions."""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.serializers.commission import CommissionSerializer


class CommissionList(generics.ListAPIView):
    """Lists all Commissions."""

    permission_classes = [AllowAny]
    serializer_class = CommissionSerializer

    def get_queryset(self):
        """GET : Lists all commissions."""
        return Commission.objects.all()
