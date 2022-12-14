"""
Views linked to links between users and associations.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.user import User
from plana.apps.users.serializers.association_users import (
    AssociationUsersCreationSerializer,
    AssociationUsersSerializer,
)


class AssociationUsersListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all associations linked to a user, or all associations of all users.

    POST : Creates a new link between a non-validated user and an association.
    """

    serializer_class = AssociationUsersCreationSerializer

    def get_queryset(self):
        if self.request.user.is_svu_manager or self.request.user.is_crous_manager:
            queryset = AssociationUsers.objects.all()
        else:
            queryset = AssociationUsers.objects.filter(user_id=self.request.user.pk)
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
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
        association_users = AssociationUsers.objects.filter(
            user_id=user.pk, association_id=association_id
        )
        if association_users.count() > 0:
            return response.Response(
                {"error": _("User already in association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            (request.user.is_anonymous and user.is_validated_by_admin)
            or (
                not request.user.is_anonymous
                and not request.user.is_svu_manager
                and not request.user.is_crous_manager
            )
            or (user.is_svu_manager or user.is_crous_manager or user.is_superuser)
        ):
            return response.Response(
                {"error": _("Associations for this user cannot be edited.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class AssociationUsersRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all associations linked to a user (manager).

    DELETE : Deletes an association linked to a user (manager).
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            serializer = self.serializer_class(
                self.queryset.filter(user_id=kwargs["user_id"]), many=True
            )
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return response.Response(serializer.data)


class AssociationUsersDestroy(generics.DestroyAPIView):
    """
    GET : Lists all associations linked to a user (manager).

    DELETE : Deletes an association linked to a user (manager).
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            try:
                User.objects.get(id=kwargs["user_id"])
                Association.objects.get(id=kwargs["association_id"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("No user or association found.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            AssociationUsers.objects.filter(
                user_id=kwargs["user_id"], association_id=kwargs["association_id"]
            ).delete()
            return response.Response({}, status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )
