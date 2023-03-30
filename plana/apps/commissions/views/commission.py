"""Views directly linked to commissions."""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.serializers.commission import CommissionSerializer


class CommissionList(generics.ListAPIView):
    """/commissions/ route"""

    permission_classes = [AllowAny]
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer

    def get(self, request, *args, **kwargs):
        """Lists all commission types."""
        return self.list(request, *args, **kwargs)
