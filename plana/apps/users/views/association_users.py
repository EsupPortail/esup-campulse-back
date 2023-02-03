"""
Views linked to links between users and associations.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import AssociationUsers, User
from plana.apps.users.serializers.association_users import (
    AssociationUsersCreationSerializer,
    AssociationUsersSerializer,
    AssociationUsersUpdateSerializer,
)
from plana.utils import to_bool


class AssociationUsersListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all associations linked to a user, or all associations of all users.

    POST : Creates a new link between a non-validated user and an association.
    """

    serializer_class = AssociationUsersCreationSerializer

    def get_queryset(self):
        if self.request.user.has_perm("users.view_associationusers_anyone"):
            queryset = AssociationUsers.objects.all()
        else:
            queryset = AssociationUsers.objects.filter(user_id=self.request.user.pk)
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            username = request.data["user"]
            association_id = request.data["association"]
            user = User.objects.get(username=username)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No user name or association id given.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit associations for this account.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        association_users = AssociationUsers.objects.filter(
            user_id=user.pk, association_id=association_id
        )
        if association_users.count() > 0:
            return response.Response(
                {"error": _("User already in association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_superuser or user.is_staff:
            return response.Response(
                {"error": _("A manager cannot have an association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "is_president" in request.data
            and to_bool(request.data["is_president"]) is True
        ):
            association_user_president = AssociationUsers.objects.filter(
                association_id=association_id, is_president=True
            )
            if association_user_president.count() > 0:
                return response.Response(
                    {"error": _("President already in association.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if (
            not request.user.is_anonymous
            and not request.user.is_staff
            and user.is_validated_by_admin
        ):
            return response.Response(
                {"error": _("Only managers can edit associations.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class AssociationUsersRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all associations linked to a user (manager).
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get(self, request, *args, **kwargs):
        if (
            request.user.has_perm("users.view_associationusers_anyone")
            or kwargs["user_id"] == request.user.pk
        ):
            serializer = self.serializer_class(
                self.queryset.filter(user_id=kwargs["user_id"]), many=True
            )
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return response.Response(serializer.data)


@extend_schema(methods=["PUT", "GET"], exclude=True)
class AssociationUsersUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH : Updates user role in an association (manager and president).

    DELETE : Deletes an association linked to a user (manager).
    """

    queryset = AssociationUsers.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = AssociationUsersUpdateSerializer
        else:
            self.serializer_class = AssociationUsersSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        try:
            User.objects.get(id=kwargs["user_id"])
            Association.objects.get(id=kwargs["association_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or association found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            asso_user = self.queryset.get(
                user_id=kwargs["user_id"], association_id=kwargs["association_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Link between this user and association does not exist.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            president = AssociationUsers.objects.get(
                association_id=kwargs["association_id"], user_id=request.user.pk
            ).is_president
        except ObjectDoesNotExist:
            president = False

        if (
            request.user.has_perm("users.change_associationusers_any_institution")
            or request.user.is_staff_in_institution(kwargs["association_id"])
            or request.user.is_president_in_association(kwargs["association_id"])
        ):
            if 'role_name' in request.data:
                asso_user.role_name = request.data['role_name']

            if 'is_president' in request.data and to_bool(request.data['is_president']):
                if president:
                    actual_president = AssociationUsers.objects.get(
                        association_id=kwargs["association_id"], user_id=request.user.pk
                    )
                    asso_user.is_president = True
                    actual_president.is_president = False
                    actual_president.save()
                elif request.user.is_staff_in_institution(kwargs["association_id"]):
                    try:
                        actual_president = AssociationUsers.objects.get(
                            association_id=kwargs["association_id"], is_president=True
                        )
                        actual_president.is_president = False
                        actual_president.save()
                    except ObjectDoesNotExist:
                        pass
                    asso_user.is_president = True

            if 'is_president' in request.data and not to_bool(
                request.data['is_president']
            ):
                if president:
                    return response.Response({}, status=status.HTTP_400_BAD_REQUEST)
                elif request.user.is_staff_in_institution(kwargs["association_id"]):
                    asso_user.is_president = False

            if 'can_be_president' in request.data:
                asso_user.can_be_president = to_bool(request.data['can_be_president'])

            asso_user.save()
            return response.Response({}, status=status.HTTP_200_OK)

        return response.Response({}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        try:
            User.objects.get(id=kwargs["user_id"])
            association = Association.objects.get(id=kwargs["association_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or association found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not request.user.has_perm("users.delete_associationusers_any_institution")
            and not request.user.is_staff_in_institution(association.institution_id)
            and request.user.pk != kwargs["user_id"]
        ):
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        AssociationUsers.objects.filter(
            user_id=kwargs["user_id"], association_id=kwargs["association_id"]
        ).delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
