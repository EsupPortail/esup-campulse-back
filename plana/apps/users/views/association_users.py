from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.user import User
from plana.apps.users.serializers.association_users import AssociationUsersSerializer
from plana.apps.users.serializers.association_users import (
    AssociationUsersCreationSerializer,
)


class AssociationUsersListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all associations linked to all users or associations of an authenticated user.
    POST : Creates a new link between a user and an association.
    """

    serializer_class = AssociationUsersCreationSerializer

    def get_queryset(self):
        if self.request.user.is_student:
            queryset = AssociationUsers.objects.filter(user_id=self.request.user.pk)
        else:
            queryset = AssociationUsers.objects.all()
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super(AssociationUsersListCreate, self).get_permissions()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.data["user"])

        if user.is_validated_by_admin:
            return response.Response(
                {"error": _("Associations for this user cannot be edited.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO Add UserAssociation object creation with checks here
        return super(AssociationUsersListCreate, self).create(request, *args, **kwargs)


class AssociationUsersRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all associations linked to a user.
    """

    serializer_class = AssociationUsersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_student:
            queryset = AssociationUsers.objects.filter(user_id=self.request.user.pk)
        else:
            queryset = AssociationUsers.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if "pk" in kwargs.keys():
            serializer = self.serializer_class(
                queryset.filter(user_id=kwargs["pk"]), many=True
            )
        else:
            serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data)
