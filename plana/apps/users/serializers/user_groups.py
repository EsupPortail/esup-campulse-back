from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from plana.apps.users.models.user import User


class UserGroupsSerializer(serializers.ModelSerializer):
    groups = serializers.ListField(child=serializers.IntegerField(), required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "groups",
        ]
