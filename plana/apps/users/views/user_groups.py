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
        return super(UserGroupsListCreate, self).get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = GroupSerializer
        else:
            self.serializer_class = UserGroupsSerializer
        return super(UserGroupsListCreate, self).get_serializer_class()

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.data["username"])

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


class UserGroupsRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all groups linked to a user (manager).
    """

    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Group.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        if request.user.is_student:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            serializer = self.serializer_class(
                self.get_queryset().filter(user=kwargs["pk"]), many=True
            )
        return response.Response(serializer.data)
