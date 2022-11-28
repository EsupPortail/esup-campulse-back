from rest_framework import serializers

from plana.apps.associations.models.social_network import SocialNetwork
from plana.apps.associations.serializers.association import SimpleAssociationDataSerializer


class SocialNetworkSerializer(serializers.ModelSerializer):
    association = SimpleAssociationDataSerializer()
    
    class Meta:
        model = SocialNetwork
        fields = "__all__"
