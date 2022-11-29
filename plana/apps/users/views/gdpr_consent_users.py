from django.utils.translation import gettext_lazy as _

from rest_framework import generics, response
from rest_framework.permissions import IsAuthenticated

from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.serializers.gdpr_consent_users import GDPRConsentUsersSerializer


class UserConsentsCreate(generics.CreateAPIView):
    """
    POST : Creates a new link between an user and a GDPR consent.
    """

    serializer_class = GDPRConsentUsersSerializer
    queryset = GDPRConsentUsers.objects.all()
    permission_classes = [IsAuthenticated]


class UserConsentsList(generics.RetrieveAPIView):
    """
    GET : Lists all GDPR consents linked to an user.
    """

    serializer_class = GDPRConsentUsersSerializer
    queryset = GDPRConsentUsers.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset.filter(user_id=kwargs["pk"]), many=True
        )
        return response.Response(serializer.data)
