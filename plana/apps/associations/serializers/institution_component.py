from rest_framework import serializers

from plana.apps.associations.models.institution_component import InstitutionComponent


class InstitutionComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionComponent
        fields = "__all__"
