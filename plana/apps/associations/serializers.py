from rest_framework import serializers
from .models import Association, Institution, InstitutionComponent, ActivityField


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


class AssociationSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()
    institution_component = InstitutionComponentSerializer()
    activity_field = ActivityFieldSerializer()

    class Meta:
        model = Association
        fields = "__all__"
