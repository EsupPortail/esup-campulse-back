"""Views directly linked to institutions."""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.serializers.institution import InstitutionSerializer


class InstitutionList(generics.ListAPIView):
    """Lists all institutions."""

    permission_classes = [AllowAny]
    serializer_class = InstitutionSerializer

    def get_queryset(self):
        """GET : Lists all institutions."""
        return Institution.objects.all().order_by("name")
