"""
Serializers describing fields used on associations.
"""
import json

from rest_framework import serializers

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.models.institution import Institution
from plana.apps.associations.models.institution_component import InstitutionComponent
from plana.apps.associations.models.social_network import SocialNetwork
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer
from plana.apps.associations.serializers.institution import InstitutionSerializer
from plana.apps.associations.serializers.institution_component import (
    InstitutionComponentSerializer,
)
from plana.apps.associations.serializers.social_network import (
    SocialNetworkNoIdSerializer,
    SocialNetworkSerializer,
)


class AssociationAllDataSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    institution = InstitutionSerializer()
    institution_component = InstitutionComponentSerializer()
    activity_field = ActivityFieldSerializer()
    social_networks = SocialNetworkSerializer(many=True)

    class Meta:
        model = Association
        fields = "__all__"


class AssociationAllDataNoSubTableSerializer(serializers.ModelSerializer):
    """
    Serializer without name details about sub-tables.
    """

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all()
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all()
    )
    social_networks = SocialNetworkSerializer(many=True)

    class Meta:
        model = Association
        fields = "__all__"

    def update(self, instance, validated_data):
        """
        Overrided update to manage nested social network fields.
        """
        if self.initial_data.get('social_networks'):
            old_social_networks = instance.social_networks.all()
            new_social_networks = json.loads(
                f"[{self.initial_data['social_networks']}]"
            )
            serializer = SocialNetworkNoIdSerializer(
                data=new_social_networks, many=True
            )
            if serializer.is_valid():
                old_social_networks.delete()
                for new_social_network in new_social_networks:
                    SocialNetwork.objects.create(
                        type=new_social_network["type"],
                        location=new_social_network["location"],
                        association_id=instance.id,
                    )
        instance = super().update(instance, validated_data)
        return instance


class AssociationPartialDataSerializer(serializers.ModelSerializer):
    """
    Smaller serializer to return only some of the informations of an association
    (used in a table list of all associations).
    """

    institution = InstitutionSerializer()
    institution_component = InstitutionComponentSerializer()
    activity_field = ActivityFieldSerializer()

    class Meta:
        model = Association
        fields = [
            "id",
            "institution",
            "institution_component",
            "activity_field",
            "name",
            "acronym",
            "is_enabled",
            "is_site",
        ]


class AssociationMandatoryDataSerializer(serializers.ModelSerializer):
    """
    Smaller serializer to return only the main informations of an association
    (used in a simple name list of all associations).
    """

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
        ]
