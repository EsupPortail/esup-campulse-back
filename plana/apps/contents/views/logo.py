"""Views directly linked to logos."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.contents.models.logo import Logo
from plana.apps.contents.serializers.logo import LogoSerializer


class LogoList(generics.ListAPIView):
    """/contents/logos route."""

    permission_classes = [AllowAny]
    queryset = Logo.objects.all().order_by("id")
    serializer_class = LogoSerializer
