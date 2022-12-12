"""
Serializers describing fields used on associations.
"""
from rest_framework import serializers

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer
from plana.apps.associations.serializers.institution import InstitutionSerializer
from plana.apps.associations.serializers.institution_component import (
    InstitutionComponentSerializer,
)
from plana.apps.associations.serializers.social_network import SocialNetworkSerializer


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
