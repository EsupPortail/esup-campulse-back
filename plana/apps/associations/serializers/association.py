"""Serializers describing fields used on associations."""
import re

from rest_framework import serializers

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.fields import ThumbnailField
from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.users.models.user import AssociationUser


class AssociationAllDataReadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all()
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all()
    )
    path_logo = ThumbnailField(sizes=["detail"])

    def to_representation(self, obj):
        request = self.context.get('request', None)
        representation = super().to_representation(obj)

        if request.user.is_anonymous or (
            not request.user.is_anonymous
            and not request.user.is_in_association(obj.id)
            and not request.user.has_perm("associations.view_association_all_fields")
        ):
            private_fields = ["phone", "president_phone", "can_submit_projects"]
            for private_field in private_fields:
                representation.pop(private_field)

        return representation

    class Meta:
        model = Association
        fields = "__all__"


class AssociationAllDataUpdateSerializer(serializers.ModelSerializer):
    """Main serializer."""

    name = serializers.CharField(required=False, allow_blank=True)
    acronym = serializers.CharField(required=False, allow_blank=True)
    social_object = serializers.CharField(required=False, allow_blank=True)
    current_projects = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    zipcode = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    siret = serializers.CharField(required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True)
    president_names = serializers.CharField(required=False, allow_blank=True)
    president_phone = serializers.CharField(required=False, allow_blank=True)
    president_email = serializers.CharField(required=False, allow_blank=True)
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, default=None
    )
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all(), allow_null=True, default=None
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all(), allow_null=True, default=None
    )

    def validate_phone(self, value):
        """Check phone field with a regex."""
        pattern = r"^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Wrong phone number format.")
        return value

    class Meta:
        model = Association
        fields = "__all__"


class AssociationPartialDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only some of the informations of an association."""

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all()
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all()
    )
    path_logo = ThumbnailField(sizes=["list"])

    class Meta:
        model = Association
        fields = [
            "id",
            "institution",
            "institution_component",
            "activity_field",
            "name",
            "acronym",
            "email",
            "is_enabled",
            "is_public",
            "is_site",
            "path_logo",
            "charter_status",
            "charter_date",
        ]


class AssociationMandatoryDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only the main informations of an association."""

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "email",
            "is_enabled",
            "is_public",
            "is_site",
            "institution",
        ]


class AssociationNameSerializer(serializers.ModelSerializer):
    """Smaller serializer used in a simple name list of all associations."""

    has_president = serializers.SerializerMethodField("is_president_in_association")

    def is_president_in_association(self, association) -> bool:
        """Check if a president has been linked to an association."""
        return AssociationUser.objects.filter(
            association_id=association.id, is_president=True
        ).exists()

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "has_president",
            "institution",
        ]


class AssociationStatusSerializer(serializers.ModelSerializer):
    """Serializer for status field."""

    class Meta:
        model = Association
        fields = ["charter_status"]
