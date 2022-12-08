from rest_framework import serializers

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer
from plana.apps.associations.serializers.institution import InstitutionSerializer
from plana.apps.associations.serializers.institution_component import (
    InstitutionComponentSerializer,
)
from plana.apps.associations.serializers.social_network import SocialNetworkSerializer


class AssociationListSerializer(serializers.ModelSerializer):
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


class AssociationDetailSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()
    institution_component = InstitutionComponentSerializer()
    activity_field = ActivityFieldSerializer()
    social_networks = SocialNetworkSerializer(many=True)

    class Meta:
        model = Association
        fields = "__all__"


class SimpleAssociationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "acronym",
        ]
