from rest_framework import generics
from django.contrib.auth.models import Group
from plana.apps.groups.serializers.group import GroupSerializer


class GroupList(generics.ListCreateAPIView):
    """
    GET : Lists all users groups.
    POST : Creates a new user group.
    """

    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.all()
