"""Views directly linked to institutions."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.serializers.institution import InstitutionSerializer


class InstitutionList(generics.ListAPIView):
    """/institutions/ route"""

    permission_classes = [AllowAny]
    queryset = Institution.objects.all().order_by("name")
    serializer_class = InstitutionSerializer

    def get(self, request, *args, **kwargs):
        """Lists all institutions."""
        return self.list(request, *args, **kwargs)
