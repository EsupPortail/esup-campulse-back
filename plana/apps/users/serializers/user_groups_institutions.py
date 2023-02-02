"""
Serializers describing fields used on links between users and auth groups.
"""
from django.contrib.auth.models import Group
from rest_framework import serializers

from plana.apps.users.models.user import User


class UserGroupsInstitutionsSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    groups = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field="id", queryset=Group.objects.all()
        ),
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "groups",
        ]
