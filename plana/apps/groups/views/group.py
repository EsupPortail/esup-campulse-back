"""Views directly linked to auth groups."""

from django.contrib.auth.models import Group
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.groups.serializers.group import GroupSerializer


class GroupList(generics.ListAPIView):
    """/groups/ route"""

    permission_classes = [AllowAny]
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        """Lists all groups."""
        return self.list(request, *args, **kwargs)
