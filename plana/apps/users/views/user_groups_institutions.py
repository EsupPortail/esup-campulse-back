"""
Views linked to links between users and auth groups.
"""
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.groups.serializers.group import GroupSerializer
from plana.apps.users.models.user import GroupInstitutionUsers, User
from plana.apps.users.serializers.user_groups_institutions import (
    UserGroupsInstitutionsSerializer,
)


class UserGroupsInstitutionsListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all groups linked to a user (student), or all groups of all users (manager).

    POST : Creates a new link between a non-validated user and a group.
    """

    def get_queryset(self):
        queryset = self.request.user.groups.all()
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = GroupSerializer
        else:
            self.serializer_class = UserGroupsInstitutionsSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("view_groupinstitutionusers_anyone"):
            return self.list(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def post(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            groups_ids = request.data["groups"]
            user = User.objects.get(username=username)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No user name or groups ids given.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit groups for this account.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_superuser or user.is_staff:
            return response.Response(
                {"error": _("Groups for a manager cannot be changed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not request.user.is_anonymous
            and not request.user.is_staff
            and user.is_validated_by_admin
        ):
            return response.Response(
                {"error": _("Only managers can edit groups.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        groups = (
            groups_ids
            if isinstance(groups_ids, list)
            else list(map(int, groups_ids.split(",")))
        )
        for id_group in groups:
            group = Group.objects.get(id=id_group)
            if not group.startsWith("MANAGER_"):
                GroupInstitutionUsers.objects.add(
                    user_id=user.pk, group_id=id_group, institution_id=None
                )

        return response.Response({}, status=status.HTTP_200_OK)


class UserGroupsInstitutionsRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all groups linked to a user (manager).
    """

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        if (
            request.user.has_perm("view_groupinstitutionusers_anyone")
            or kwargs["user_id"] == request.user.pk
        ):
            serializer = self.serializer_class(
                self.get_queryset().filter(user=kwargs["user_id"]), many=True
            )
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return response.Response(serializer.data)


class UserGroupsInstitutionsDestroy(generics.DestroyAPIView):
    """
    DELETE : Deletes a group linked to a user (manager).
    """

    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = GroupSerializer

    def delete(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["user_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_superuser or user.is_staff:
            return response.Response(
                {"error": _("Groups for a manager cannot be changed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.groups.count() > 1:
            GroupInstitutionUsers.objects.remove(
                user_id=user.pk, group_id=kwargs["group_id"]
            )
            return response.Response({}, status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            {"error": _("User should have at least one group.")},
            status=status.HTTP_400_BAD_REQUEST,
        )
