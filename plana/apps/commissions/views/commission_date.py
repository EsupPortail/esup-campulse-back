"""Views linked to commissions dates."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer


class CommissionDateList(generics.ListAPIView):
    """/commissions/commission_dates route"""

    permission_classes = [AllowAny]
    queryset = CommissionDate.objects.all().order_by("submission_date")
    serializer_class = CommissionDateSerializer

    def get(self, request, *args, **kwargs):
        """Lists all commission dates."""
        return self.list(request, *args, **kwargs)
