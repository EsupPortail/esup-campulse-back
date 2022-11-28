from rest_framework import serializers

from plana.apps.associations.models.institution import Institution


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = "__all__"
