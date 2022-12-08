from rest_framework import serializers

from plana.apps.associations.models.social_network import SocialNetwork


class SocialNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialNetwork
        fields = [
            "id",
            "type",
            "location",
        ]
