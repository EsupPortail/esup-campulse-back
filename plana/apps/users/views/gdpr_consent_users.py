from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User
from plana.apps.users.serializers.gdpr_consent_users import GDPRConsentUsersSerializer


class UserConsentsListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all consents linked to a user (student), or all consents of all users (manager).

    POST : Creates a new link between a user and a consent (authenticated).
    """

    serializer_class = GDPRConsentUsersSerializer
    queryset = GDPRConsentUsers.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_student:
            queryset = GDPRConsentUsers.objects.filter(user_id=self.request.user.pk)
        else:
            queryset = GDPRConsentUsers.objects.all()
        return queryset

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.data["user"])
        consent_users = GDPRConsentUsers.objects.filter(
            user_id=user.pk, consent_id=request.data["consent"]
        )
        if consent_users.count() > 0:
            return response.Response(
                {"error": _("User already consented.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super(UserConsentsListCreate, self).create(request, *args, **kwargs)


class UserConsentsRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists all GDPR consents linked to a user (manager).
    """

    serializer_class = GDPRConsentUsersSerializer
    queryset = GDPRConsentUsers.objects.all()
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
