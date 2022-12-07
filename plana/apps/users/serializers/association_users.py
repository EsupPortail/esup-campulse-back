from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from plana.apps.associations.serializers.association import (
    SimpleAssociationDataSerializer,
)
from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.user import User


class AssociationUsersSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    association = SimpleAssociationDataSerializer()

    class Meta:
        model = AssociationUsers
        fields = [
            "id",
            "user",
            "role_name",
            "has_office_status",
            "is_president",
            "association",
        ]


class AssociationUsersCreationSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = AssociationUsers
        fields = [
            "user",
            "role_name",
            "has_office_status",
            "is_president",
            "association",
        ]
