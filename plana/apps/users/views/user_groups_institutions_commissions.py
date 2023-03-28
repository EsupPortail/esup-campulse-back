"""Views linked to links between users and auth groups."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission import Commission
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import (
    AssociationUsers,
    GroupInstitutionCommissionUsers,
    User,
)
from plana.apps.users.serializers.user_groups_institutions_commissions import (
    UserGroupsInstitutionsCommissionsCreateSerializer,
    UserGroupsInstitutionsCommissionsSerializer,
)


@extend_schema_view(
    get=extend_schema(tags=["users/groups"]),
    post=extend_schema(tags=["users/groups"]),
)
class UserGroupsInstitutionsCommissionsListCreate(generics.ListCreateAPIView):
    """/users/groups/ route"""

    queryset = GroupInstitutionCommissionUsers.objects.all()
    serializer_class = UserGroupsInstitutionsCommissionsCreateSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """Lists all groups linked to a user, or all groups of all users (manager)."""
        if request.user.has_perm(
            "users.view_groupinstitutioncommissionusers_any_group"
        ):
            serializer = self.serializer_class(
                GroupInstitutionCommissionUsers.objects.all(), many=True
            )
            return response.Response(serializer.data)
        serializer = self.serializer_class(
            GroupInstitutionCommissionUsers.objects.filter(user_id=request.user.pk),
            many=True,
        )
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Creates a new link between a non-validated user and a group."""
        try:
            group_id = request.data["group"]
            group = Group.objects.get(pk=group_id)
            user = User.objects.get(username=request.data["username"])
            institution = None
            institution_id = None
            if (
                "institution" in request.data
                and request.data["institution"] is not None
            ):
                institution = Institution.objects.get(id=request.data["institution"])
                institution_id = institution.id
            commission = None
            commission_id = None
            if "commission" in request.data and request.data["commission"] is not None:
                commission = Commission.objects.get(id=request.data["commission"])
                commission_id = commission.id
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("Wrong ids given.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit groups for this account.")},
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

        if (user.is_superuser or user.is_staff) and not request.user.has_perm(
            "users.add_groupinstitutioncommissionusers_any_group"
        ):
            return response.Response(
                {"error": _("Groups for a manager cannot be changed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group_structure = settings.GROUPS_STRUCTURE[group.name]
        if (
            group_structure["REGISTRATION_ALLOWED"] is False
            and not request.user.has_perm(
                "users.add_groupinstitutioncommissionusers_any_group"
            )
            and (
                not request.user.is_staff
                or (request.user.is_staff and group in request.user.get_user_groups())
            )
        ):
            return response.Response(
                {"error": _("Registering in this group is not allowed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if institution_id is not None:
            if (group_structure["INSTITUTION_ID_POSSIBLE"] is False) or (
                not request.user.has_perm(
                    "users.add_groupinstitutioncommissionusers_any_group"
                )
                and (
                    not request.user.is_anonymous
                    and not institution in request.user.get_user_institutions()
                )
            ):
                return response.Response(
                    {"error": _("Adding institution in this group is not possible.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if commission_id is not None:
            if (group_structure["COMMISSION_ID_POSSIBLE"] is False) or (
                not request.user.has_perm(
                    "users.add_groupinstitutioncommissionusers_any_group"
                )
                and (
                    not request.user.is_anonymous
                    and not commission.institution_id
                    in request.user.get_user_institutions()
                )
            ):
                return response.Response(
                    {"error": _("Adding commission in this group is not possible.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        GroupInstitutionCommissionUsers.objects.create(
            user_id=user.pk,
            group_id=group_id,
            institution_id=institution_id,
            commission_id=commission_id,
        )

        return response.Response({}, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(tags=["users/groups"]),
)
class UserGroupsInstitutionsCommissionsRetrieve(generics.RetrieveAPIView):
    """/users/{user_id}/groups/ route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionCommissionUsers.objects.all()
    serializer_class = UserGroupsInstitutionsCommissionsSerializer

    def get(self, request, *args, **kwargs):
        """Lists all groups linked to a user (manager)."""
        if request.user.has_perm(
            "users.view_groupinstitutioncommissionusers_any_group"
        ):
            serializer = self.serializer_class(
                GroupInstitutionCommissionUsers.objects.filter(
                    user_id=kwargs["user_id"]
                ),
                many=True,
            )
            return response.Response(serializer.data)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )


# TODO Optimize this route to avoid code duplication with other delete routes.
@extend_schema_view(
    delete=extend_schema(operation_id="users_groups_destroy", tags=["users/groups"])
)
class UserGroupsInstitutionsCommissionsDestroy(generics.DestroyAPIView):
    """/users/{user_id}/groups/{group_id}"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionCommissionUsers.objects.all()
    serializer_class = UserGroupsInstitutionsCommissionsSerializer

    def delete(self, request, *args, **kwargs):
        """Destroys a group linked to a user (manager)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionCommissionUsers.objects.filter(
                user_id=user.pk
            )
            user_group_to_delete = GroupInstitutionCommissionUsers.objects.filter(
                user_id=user.pk,
                group_id=kwargs["group_id"],
                institution_id=None,
                commission_id=None,
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or link to group found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group_name = Group.objects.get(id=kwargs["group_id"]).name
        if (
            settings.GROUPS_STRUCTURE[group_name]["ASSOCIATIONS_POSSIBLE"] is True
            and AssociationUsers.objects.filter(user_id=user).count() > 0
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


@extend_schema_view(
    delete=extend_schema(
        operation_id="users_groups_destroy_with_commission", tags=["users/groups"]
    )
)
class UserGroupsInstitutionsCommissionsDestroyWithCommission(generics.DestroyAPIView):
    """/users/{user_id}/groups/{group_id}/commissions/{commission_id}"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionCommissionUsers.objects.all()
    serializer_class = UserGroupsInstitutionsCommissionsSerializer

    def delete(self, request, *args, **kwargs):
        """Destroys a group linked to a user with commission argument (manager)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionCommissionUsers.objects.filter(
                user_id=user.pk
            )
            user_group_to_delete = GroupInstitutionCommissionUsers.objects.filter(
                user_id=user.pk,
                group_id=kwargs["group_id"],
                institution_id=None,
                commission_id=kwargs["commission_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or link to group found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.has_perm(
            "users.delete_groupinstitutioncommissionusers_any_group"
        ) and (
            not Commission.objects.get(id=kwargs["commission_id"]).institution_id
            in request.user.get_user_institutions()
        ):
            return response.Response(
                {"error": _("Not allowed to delete this link between user and group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_groups.count() <= 1:
            return response.Response(
                {"error": _("User should have at least one group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_group_to_delete.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    delete=extend_schema(
        operation_id="users_groups_destroy_with_institution", tags=["users/groups"]
    )
)
class UserGroupsInstitutionsCommissionsDestroyWithInstitution(generics.DestroyAPIView):
    """/users/{user_id}/groups/{group_id}/institutions/{institution_id}"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = GroupInstitutionCommissionUsers.objects.all()
    serializer_class = UserGroupsInstitutionsCommissionsSerializer

    def delete(self, request, *args, **kwargs):
        """Destroys a group linked to a user with institution argument (manager)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            user_groups = GroupInstitutionCommissionUsers.objects.filter(
                user_id=user.pk
            )
            user_group_to_delete = GroupInstitutionCommissionUsers.objects.filter(
                user_id=user.pk,
                group_id=kwargs["group_id"],
                institution_id=kwargs["institution_id"],
                commission_id=None,
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or link to group found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.has_perm(
            "users.delete_groupinstitutioncommissionusers_any_group"
        ) and (not kwargs["institution_id"] in request.user.get_user_institutions()):
            return response.Response(
                {"error": _("Not allowed to delete this link between user and group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_groups.count() <= 1:
            return response.Response(
                {"error": _("User should have at least one group.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_group_to_delete.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
