"""Views directly linked to auth groups."""
from django.contrib.auth.models import Group
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.groups.serializers.group import GroupSerializer


class GroupList(generics.ListAPIView):
    """Lists all groups."""

    permission_classes = [AllowAny]
    serializer_class = GroupSerializer

    def get_queryset(self):
        """GET : Lists all groups."""
        return Group.objects.all().order_by("name")
