from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.user import User
from plana.apps.users.serializers.association_users import AssociationUsersSerializer
from plana.apps.users.serializers.association_users import (
    AssociationUsersCreationSerializer,
)


class AssociationUsersListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all associations linked to a user (student), or all associations of all users (manager).

    POST : Creates a new link between a non-validated user and an association.
    """

    serializer_class = AssociationUsersCreationSerializer

    def get_queryset(self):
        if self.request.user.is_student:
            queryset = AssociationUsers.objects.filter(user_id=self.request.user.pk)
        else:
            queryset = AssociationUsers.objects.all()
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
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
        association_users = AssociationUsers.objects.filter(
            user_id=user.pk, association_id=request.data["association"]
        )
        if association_users.count() > 0:
            return response.Response(
                {"error": _("User already in association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_validated_by_admin:
            return response.Response(
                {"error": _("Associations for this user cannot be edited.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(AssociationUsersListCreate, self).create(request, *args, **kwargs)


class AssociationUsersRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """
    GET : Lists all associations linked to a user (manager).
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_student:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            serializer = self.serializer_class(
                self.queryset.filter(user_id=kwargs["pk"]), many=True
            )
        return response.Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if request.user.is_student:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            self.destroy(request, *args, **kwargs)
            return response.Response({}, status=status.HTTP_204_NO_CONTENT)
