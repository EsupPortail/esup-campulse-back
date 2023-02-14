"""
Views linked to links between users and auth groups.
"""
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.users.models.user import GroupInstitutionUsers, User
from plana.apps.users.serializers.user_groups_institutions import (
    UserGroupsInstitutionsCreateSerializer,
    UserGroupsInstitutionsSerializer,
)


class UserGroupsInstitutionsListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all groups linked to a user (student), or all groups of all users (manager).

    POST : Creates a new link between a non-validated user and a group.
    """

    queryset = GroupInstitutionUsers.objects.all()
    serializer_class = UserGroupsInstitutionsCreateSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("users.view_groupinstitutionusers_anyone"):
            serializer = self.serializer_class(
                GroupInstitutionUsers.objects.all(), many=True
            )
            return response.Response(serializer.data)
        serializer = self.serializer_class(
            GroupInstitutionUsers.objects.filter(user_id=request.user.pk), many=True
        )
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            # groups_ids = request.data["groups"]
            group_id = request.data["group"]
            user = User.objects.get(username=request.data["username"])
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

        # In case we revert to a multi-group linking to users system
        """
        groups = (
            groups_ids
            if isinstance(groups_ids, list)
            else list(map(int, groups_ids.split(",")))
        )
        for id_group in groups:
            try:
                group = Group.objects.get(id=id_group)
                if group.name in settings.PUBLIC_GROUPS:
                    GroupInstitutionUsers.objects.create(
                        user_id=user.pk, group_id=id_group, institution_id=None
                    )
                else:
                    return response.Response(
                        {"error": _("Adding users in this group is not allowed.")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Group.DoesNotExist:
                return response.Response(
                    {"error": _("Group does not exist.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        """
        try:
            group = Group.objects.get(pk=group_id)
            if group.name in settings.PUBLIC_GROUPS:
                GroupInstitutionUsers.objects.create(
                    user_id=user.pk, group_id=group_id, institution_id=None
                )
            else:
                return response.Response(
                    {"error": _("Adding users in this group is not allowed.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Group.DoesNotExist:
            return response.Response(
                {"error": _("Group does not exist.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return response.Response({}, status=status.HTTP_200_OK)


class UserGroupsInstitutionsRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all groups linked to a user (manager).
    """

    queryset = GroupInstitutionUsers.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = UserGroupsInstitutionsSerializer

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("users.view_groupinstitutionusers_anyone"):
            serializer = self.serializer_class(
                GroupInstitutionUsers.objects.filter(user_id=kwargs["user_id"]),
                many=True,
            )
            return response.Response(serializer.data)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )


class UserGroupsInstitutionsDestroy(generics.DestroyAPIView):
    """
    DELETE : Deletes a group linked to a user (manager).
    """

    queryset = GroupInstitutionUsers.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = UserGroupsInstitutionsSerializer

    def delete(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionUsers.objects.filter(user_id=user.pk)
            user_group_to_delete = GroupInstitutionUsers.objects.get(
                user_id=user.pk, group_id=kwargs["group_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or link to group found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_superuser or user.is_staff:
            return response.Response(
                {"error": _("Groups for a manager cannot be changed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_groups.count() > 1:
            user_group_to_delete.delete()
            return response.Response({}, status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            {"error": _("User should have at least one group.")},
            status=status.HTTP_400_BAD_REQUEST,
        )
