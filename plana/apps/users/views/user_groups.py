from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import UserSerializer
from plana.apps.users.serializers.user_groups import UserGroupsSerializer


class UserGroupsCreate(generics.CreateAPIView):
    """
    POST : Creates a new link between a user and a group.
    """

    serializer_class = UserGroupsSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.data["username"])
        serializer = self.serializer_class(instance=user)

        if user.is_validated_by_admin:
            return response.Response(
                {"error": _("Groups for this user cannot be edited.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        groups = (
            request.data["groups"]
            if type(request.data["groups"]) == list
            else list(map(int, request.data["groups"].split(",")))
        )
        for id_group in groups:
            try:
                group = Group.objects.get(id=id_group)
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Group not found.")}, status=status.HTTP_400_BAD_REQUEST
                )
            user.groups.add(group)

        return response.Response({}, status=status.HTTP_200_OK)


class UserGroupsList(generics.ListAPIView):
    """
    GET : Lists all groups linked to a user.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs["pk"])
        serializer = self.serializer_class(instance=user)
        return response.Response(serializer.data["groups"])
