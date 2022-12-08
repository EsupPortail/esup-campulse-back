from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.groups.serializers.group import GroupSerializer
from plana.apps.users.models.user import User
from plana.apps.users.serializers.user_groups import UserGroupsSerializer


class UserGroupsListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all groups linked to a user (student), or all groups of all users (manager).

    POST : Creates a new link between a non-validated user and a group.
    """

    def get_queryset(self):
        queryset = self.request.user.groups.all()
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = GroupSerializer
        else:
            self.serializer_class = UserGroupsSerializer
        return super().get_serializer_class()

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.data["username"])

        if user.is_validated_by_admin:
            return response.Response(
                {"error": _("Groups for this user cannot be edited.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        groups = (
            request.data["groups"]
            if isinstance(request.data["groups"], list)
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


class UserGroupsRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all groups linked to a user (manager).
    """

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            serializer = self.serializer_class(
                self.get_queryset().filter(user=kwargs["pk"]), many=True
            )
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return response.Response(serializer.data)


class UserGroupsDestroy(generics.DestroyAPIView):
    """
    DELETE : Deletes a group linked to a user (manager).
    """

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def delete(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            user = User.objects.get(id=kwargs["user_id"])
            if user.groups.count() > 1:
                user.groups.remove(kwargs["group_id"])
                return response.Response({}, status=status.HTTP_204_NO_CONTENT)
            return response.Response(
                {"error": _("User should have at least one group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
