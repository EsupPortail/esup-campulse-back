"""
Serializers describing fields used on links between users and GDPR consents.
"""
from rest_framework import serializers

from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User


class GDPRConsentUsersSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    # user = UserRelatedField(queryset=User.objects.all(), many=False)

    class Meta:
        model = GDPRConsentUsers
        fields = "__all__"
