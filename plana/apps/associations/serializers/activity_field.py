from rest_framework import serializers

from plana.apps.associations.models.activity_field import ActivityField


class ActivityFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityField
        fields = "__all__"
