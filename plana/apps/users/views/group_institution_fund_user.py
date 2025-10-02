"""Views linked to links between users and auth groups."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.fund import Fund
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User
from plana.apps.users.serializers.group_institution_fund_user import (
    GroupInstitutionFundUserCreateSerializer,
    GroupInstitutionFundUserSerializer,
)


@extend_schema_view(
    get=extend_schema(tags=["users/groups"]),
    post=extend_schema(tags=["users/groups"])
)
class GroupInstitutionFundUserListCreate(generics.ListCreateAPIView):
    """/users/groups/ route."""

    queryset = GroupInstitutionFundUser.objects.all()
    serializer_class = GroupInstitutionFundUserCreateSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @extend_schema(
        responses={
            status.HTTP_200_OK: GroupInstitutionFundUserCreateSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["users/groups"],
    )
    def get(self, request, *args, **kwargs):
        """List all groups linked to a user, or all groups of all users (manager)."""
        if request.user.has_perm("users.view_groupinstitutionfunduser_any_group"):
            serializer = self.serializer_class(self.queryset.all(), many=True)
            return response.Response(serializer.data)
        serializer = self.serializer_class(
            self.queryset.filter(user_id=request.user.pk),
            many=True,
        )
        return response.Response(serializer.data)


class GroupInstitutionFundUserRetrieve(generics.RetrieveAPIView):
    """/users/{user_id}/groups/ route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionFundUser.objects.all()
    serializer_class = GroupInstitutionFundUserSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: GroupInstitutionFundUserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/groups"],
    )
    def get(self, request, *args, **kwargs):
        """List all groups linked to a user (manager)."""
        get_object_or_404(User, id=kwargs["user_id"])

        if not request.user.has_perm("users.view_groupinstitutionfunduser_any_group"):
            return response.Response(
                {"error": _("Not allowed to get this link between group and user.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.serializer_class(
            self.queryset.filter(user_id=kwargs["user_id"]),
            many=True,
        )
        return response.Response(serializer.data)


class GroupInstitutionFundUserDestroy(generics.DestroyAPIView):
    """/users/{user_id}/groups/{group_id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionFundUser.objects.all()
    serializer_class = GroupInstitutionFundUserSerializer

    @extend_schema(
        operation_id="users_groups_destroy",
        responses={
            status.HTTP_204_NO_CONTENT: GroupInstitutionFundUserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/groups"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a group linked to a user (manager)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionFundUser.objects.filter(user_id=user.id)
            user_group_to_delete = GroupInstitutionFundUser.objects.get(
                user_id=user.id,
                group_id=kwargs["group_id"],
                institution_id=None,
                fund_id=None,
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User or link does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        group_name = Group.objects.get(id=kwargs["group_id"]).name
        if (
            settings.GROUPS_STRUCTURE[group_name]["ASSOCIATIONS_POSSIBLE"]
            and AssociationUser.objects.filter(user_id=user).exists()
        ):
            return response.Response(
                {"error": _("User is still linked to an association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_groups.count() <= 1:
            return response.Response(
                {"error": _("User should have at least one group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_group_to_delete.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)


class GroupInstitutionFundUserDestroyWithFund(generics.DestroyAPIView):
    """/users/{user_id}/groups/{group_id}/funds/{fund_id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionFundUser.objects.all()
    serializer_class = GroupInstitutionFundUserSerializer

    @extend_schema(
        operation_id="users_groups_destroy_with_fund",
        responses={
            status.HTTP_204_NO_CONTENT: GroupInstitutionFundUserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/groups"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a group linked to a user with fund argument (manager)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionFundUser.objects.filter(user_id=user.id)
            user_group_to_delete = GroupInstitutionFundUser.objects.get(
                user_id=user.id,
                group_id=kwargs["group_id"],
                institution_id=None,
                fund_id=kwargs["fund_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User or link does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("users.delete_groupinstitutionfunduser_any_group") and (
            not Fund.objects.get(id=kwargs["fund_id"]).institution_id in request.user.get_user_managed_institutions()
        ):
            return response.Response(
                {"error": _("Not allowed to delete this link between user and group.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        # The user can only delete an assignation if he still has at least 1 group after deletion
        if user_groups.count() <= 1:
            return response.Response(
                {"error": _("User should have at least one group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_group_to_delete.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)


class GroupInstitutionFundUserDestroyWithInstitution(generics.DestroyAPIView):
    """/users/{user_id}/groups/{group_id}/institutions/{institution_id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionFundUser.objects.all()
    serializer_class = GroupInstitutionFundUserSerializer

    @extend_schema(
        operation_id="users_groups_destroy_with_institution",
        responses={
            status.HTTP_204_NO_CONTENT: GroupInstitutionFundUserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/groups"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a group linked to a user with institution argument (manager)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionFundUser.objects.filter(user_id=user.id)
            user_group_to_delete = GroupInstitutionFundUser.objects.get(
                user_id=user.id,
                group_id=kwargs["group_id"],
                institution_id=kwargs["institution_id"],
                fund_id=None,
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User or link does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("users.delete_groupinstitutionfunduser_any_group") and (
            not kwargs["institution_id"] in request.user.get_user_managed_institutions()
        ):
            return response.Response(
                {"error": _("Not allowed to delete this link between user and group.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user_groups.count() <= 1:
            return response.Response(
                {"error": _("User should have at least one group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_group_to_delete.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
