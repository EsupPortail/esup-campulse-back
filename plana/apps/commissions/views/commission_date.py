"""Views linked to commissions dates."""
from rest_framework import generics

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer


class CommissionDateList(generics.ListAPIView):
    """Lists all Commissions Dates."""

    serializer_class = CommissionDateSerializer

    def get_queryset(self):
        """GET : Lists all commissions dates."""
        return CommissionDate.objects.all().order_by("submission_date")
