from rest_framework import generics
from django.contrib.auth.models import Group
from plana.apps.groups.serializers.group import GroupSerializer


class GroupList(generics.ListAPIView):
    """
    GET : Lists all users groups.
    """

    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.all().order_by("name")
