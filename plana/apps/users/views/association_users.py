from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.user import User
from plana.apps.users.serializers.association_users import AssociationUsersSerializer
from plana.apps.users.serializers.association_users import (
    AssociationUsersCreationSerializer,
)


class AssociationUsersCreate(generics.CreateAPIView):
    """
    POST : Creates a new link between a user and an association.
    """

    serializer_class = AssociationUsersCreationSerializer

    def create(self, request, *args, **kwargs):
        user = User.objects.get(username=request.data["user"])

        if user.is_validated_by_admin:
            return response.Response(
                {"error": _("Associations for this user cannot be edited.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO Add UserAssociation object creation with checks here
        return super(AssociationUsersCreate, self).create(request, *args, **kwargs)


class AssociationUsersList(generics.RetrieveAPIView):
    """
    GET : Lists all associations linked to a user.
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset.filter(user_id=kwargs["pk"]), many=True
        )
        return response.Response(serializer.data)
