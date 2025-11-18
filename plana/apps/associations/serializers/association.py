"""Serializers describing fields used on associations."""

import re

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer
from plana.apps.associations.serializers.fields import ThumbnailField
from plana.apps.associations.utils import normalize_association_name
from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.institutions.serializers.institution import InstitutionSerializer
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)
from plana.utils import PHONE_REGEX_PATTERN


class AssociationAllDataReadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    institution = InstitutionSerializer(read_only=True)
    institution_component = InstitutionComponentSerializer(read_only=True)
    activity_field = ActivityFieldSerializer(read_only=True)
    path_logo = ThumbnailField(sizes=["detail"])
    calculated_expiration_date = serializers.ReadOnlyField()

    def to_representation(self, obj):
        """Don't send confidential values depending on the user doing the request."""
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

    name = serializers.CharField(required=False, allow_blank=True, max_length=250)
    acronym = serializers.CharField(required=False, allow_blank=True, max_length=30)
    social_object = serializers.CharField(required=False, allow_blank=True)
    current_projects = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    zipcode = serializers.CharField(required=False, allow_blank=True, max_length=32)
    city = serializers.CharField(required=False, allow_blank=True, max_length=128)
    country = serializers.CharField(required=False, allow_blank=True, max_length=128)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    email = serializers.CharField(required=False, allow_blank=True, max_length=256)
    siret = serializers.CharField(required=False, allow_blank=True, max_length=14)
    website = serializers.CharField(required=False, allow_blank=True, max_length=200)
    president_names = serializers.CharField(required=False, allow_blank=True, max_length=256)
    president_phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    president_email = serializers.CharField(required=False, allow_blank=True, max_length=256)
    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all(), allow_null=True, default=None)
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all(), allow_null=True, default=None
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all(), allow_null=True, default=None
    )

    def validate_phone(self, value):
        """Check phone field with a regex."""
        if value == '':
            return value
        if not re.match(PHONE_REGEX_PATTERN, value):
            raise serializers.ValidationError("Wrong phone number format.")
        return value

    class Meta:
        model = Association
        fields = "__all__"


class AssociationPartialDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only some of the informations of an association."""

    institution = InstitutionSerializer(read_only=True)
    institution_component = InstitutionComponentSerializer(read_only=True)
    activity_field = ActivityFieldSerializer(read_only=True)
    path_logo = serializers.SerializerMethodField("cached_logo_url")

    def cached_logo_url(self, association) -> dict[str, str]:
        """Return cached logo URL instead of calculated one which is slower."""
        if association.path_logo.name != '':
            logo_name = f"{association.path_logo.name.split('.')[0]}_list.{association.path_logo.name.split('.')[1]}"
            return {
                "list": f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_PUBLIC_BUCKET_NAME}/thumbnails/{logo_name}"
            }
        return None

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
            "acronym",
            "email",
            "is_enabled",
            "is_public",
            "is_site",
            "institution",
            "can_submit_projects"
        ]

    def validate(self, data):
        user = self.context['request'].user

        if "institution" not in data:
            institutions = user.get_user_managed_institutions()
            if institutions.count() == 1:
                data["institution"] = institutions.first()
            else:
                raise serializers.ValidationError({"no_institution": _("No institution given.")})

        if not user.has_perm("associations.add_association_any_institution") and not user.is_staff_in_institution(data["institution"]):
            raise serializers.ValidationError({"wrong_institution": _("Not allowed to create an association for this institution.")})

        restricted_fields = ["is_site", "is_public"]
        if any(bool(data.get(field)) for field in restricted_fields) and not user.has_perm("associations.add_association_all_fields"):
            raise serializers.ValidationError({"restricted_fields": _("Not allowed to create an association with restricted fields.")})

        # Removes spaces, uppercase and accented characters to avoid similar association names.
        associations = Association.objects.all()
        for association in associations:
            if normalize_association_name(data["name"]) == normalize_association_name(association.name):
                raise serializers.ValidationError({"similar_name": _("Association name already taken.")})

        if "is_site" not in data:
            data["is_site"] = settings.ASSOCIATION_IS_SITE_DEFAULT
        data["is_enabled"] = True  # Always enabled at creation

        return data


class AssociationNameSerializer(serializers.ModelSerializer):
    """Smaller serializer used in a simple name list of all associations."""

    has_president = serializers.BooleanField()

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
