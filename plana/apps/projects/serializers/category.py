"""Serializers describing fields used on categories."""

from rest_framework import serializers

from plana.apps.projects.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Category
        fields = "__all__"
