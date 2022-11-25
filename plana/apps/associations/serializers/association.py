from rest_framework import serializers
from plana.apps.associations.models.association import (
    Association,
    Institution,
    InstitutionComponent,
    ActivityField,
)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = "__all__"


class InstitutionComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionComponent
        fields = "__all__"


class ActivityFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityField
        fields = "__all__"


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
