"""
Serializers describing fields used on links between users and auth groups.
"""
from django.contrib.auth.models import Group
from rest_framework import serializers

from plana.apps.institutions.serializers.institution import InstitutionSerializer
from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import GroupSerializer


class UserGroupsInstitutionsSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    group = GroupSerializer()
    institution = InstitutionSerializer()

    class Meta:
        model = User
        fields = ["id", "user", "group", "institution"]
