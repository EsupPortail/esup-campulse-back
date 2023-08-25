"""Views directly linked to logos."""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.contents.models.logo import Logo
from plana.apps.contents.serializers.logo import LogoSerializer


class LogoList(generics.ListAPIView):
    """/contents/logos route"""

    permission_classes = [AllowAny]
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: LogoSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all logos."""
        return self.list(request, *args, **kwargs)
