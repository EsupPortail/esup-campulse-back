"""Serializer describing fields used on project's comments"""

from rest_framework import serializers

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import UserNameSerializer


class ProjectCommentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.visible_objects.all())
    user = UserNameSerializer()

    class Meta:
        model = ProjectComment
        fields = "__all__"


class ProjectCommentDataSerializer(serializers.ModelSerializer):
    """Fields that can be created."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProjectComment
        fields = ["project", "is_visible", "text", "user"]


class ProjectCommentUpdateSerializer(serializers.ModelSerializer):
    """Fields that can be updated."""

    class Meta:
        model = ProjectComment
        fields = ["text", "is_visible"]
