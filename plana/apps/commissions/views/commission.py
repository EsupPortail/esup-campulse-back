"""Views directly linked to commissions."""
from rest_framework import generics

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission import CommissionSerializer
from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer


class CommissionList(generics.ListAPIView):
    """Lists all Commissions."""

    serializer_class = CommissionSerializer

    def get_queryset(self):
        """GET : Lists all commissions."""
        return Commission.objects.all()


class CommissionDateList(generics.ListAPIView):
    """Lists all Commissions Dates."""

    serializer_class = CommissionDateSerializer

    def get_queryset(self):
        """GET : Lists all commissions dates."""
        return CommissionDate.objects.all().order_by("submission_date")
