"""Views linked to links between users and auth groups."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.fund import Fund
from plana.apps.history.models.history import History
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User
from plana.apps.users.serializers.group_institution_fund_user import (
    GroupInstitutionFundUserCreateSerializer,
    GroupInstitutionFundUserSerializer,
)


class GroupInstitutionFundUserListCreate(generics.ListCreateAPIView):
    """/users/groups/ route."""

    queryset = GroupInstitutionFundUser.objects.all()
    serializer_class = GroupInstitutionFundUserCreateSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

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

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: GroupInstitutionFundUserCreateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/groups"],
    )
    def post(self, request, *args, **kwargs):
        """Create a new link between a non-validated user and a group."""
        # TODO Remove multiple is_staff checks to use another helper.
        try:
            group_id = request.data["group"]
            group = Group.objects.get(id=group_id)
            user = User.objects.get(username=request.data["user"])
            institution = None
            institution_id = None
            if "institution" in request.data and request.data["institution"] is not None:
                institution = Institution.objects.get(id=request.data["institution"])
                institution_id = institution.id
            fund = None
            fund_id = None
            if "fund" in request.data and request.data["fund"] is not None:
                fund = Fund.objects.get(id=request.data["fund"])
                fund_id = fund.id
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("User or group or institution or fund does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            GroupInstitutionFundUser.objects.filter(
                user_id=user.id,
                group_id=group_id,
                institution_id=institution_id,
                fund_id=fund_id,
            ).count()
            > 0
        ):
            return response.Response(
                {"error": _("Link between user and group does exist.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit groups for this account.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.is_anonymous and not request.user.is_staff and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit groups.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (user.is_superuser or user.is_staff) and not request.user.has_perm(
            "users.add_groupinstitutionfunduser_any_group"
        ):
            return response.Response(
                {"error": _("Groups for a manager cannot be changed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group_structure = settings.GROUPS_STRUCTURE[group.name]
        if (
            group_structure["REGISTRATION_ALLOWED"] is False
            and not request.user.has_perm("users.add_groupinstitutionfunduser_any_group")
            and (not request.user.is_staff or (request.user.is_staff and group in request.user.get_user_groups()))
        ):
            return response.Response(
                {"error": _("Registering in this group is not allowed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (group_structure["REGISTRATION_ALLOWED"] is False and user.get_user_groups().count() > 0) or (
            group_structure["REGISTRATION_ALLOWED"] is True and user.is_staff is True
        ):
            return response.Response(
                {"error": _("Cannot register in a public and a private group at the same time.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if institution_id is not None:
            if (group_structure["INSTITUTION_ID_POSSIBLE"] is False) or (
                not request.user.has_perm("users.add_groupinstitutionfunduser_any_group")
                and (not request.user.is_anonymous and not institution in request.user.get_user_managed_institutions())
            ):
                return response.Response(
                    {"error": _("Adding institution in this group is not possible.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if fund_id is not None:
            if (group_structure["FUND_ID_POSSIBLE"] is False) or (
                not request.user.has_perm("users.add_groupinstitutionfunduser_any_group")
                and (
                    not request.user.is_anonymous
                    and not fund.institution_id
                    in request.user.get_user_managed_institutions().values_list("id", flat=True)
                )
            ):
                return response.Response(
                    {"error": _("Adding fund in this group is not possible.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        gifu = GroupInstitutionFundUser.objects.create(
            user_id=user.id,
            group_id=group_id,
            institution_id=institution_id,
            fund_id=fund_id,
        )

        if not request.user.is_anonymous:
            History.objects.create(
                action_title="GROUP_INSTITUTION_FUND_USER_CHANGED",
                action_user_id=request.user.pk,
                group_institution_fund_user_id=gifu.id,
            )

        return response.Response({}, status=status.HTTP_201_CREATED)


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
        try:
            User.objects.get(id=kwargs["user_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

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
            settings.GROUPS_STRUCTURE[group_name]["ASSOCIATIONS_POSSIBLE"] is True
            and AssociationUser.objects.filter(user_id=user).count() > 0
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
