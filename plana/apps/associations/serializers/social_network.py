"""
Serializers describing fields used on social networks used by associations.
"""
from rest_framework import serializers

from plana.apps.associations.models.social_network import SocialNetwork


class SocialNetworkSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    class Meta:
        model = SocialNetwork
        fields = [
            "id",
            "type",
            "location",
        ]
