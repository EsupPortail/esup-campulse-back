"""Serializer describing fields used on project's comments"""
from rest_framework import serializers

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.users.models.user import User


class ProjectCommentSerializer(serializers.ModelSerializer):
    """Main serializer"""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProjectComment
        fields = "__all__"


class ProjectCommentDataSerializer(serializers.ModelSerializer):
    """Fields that can be updated by an administrator"""

    class Meta:
        model = ProjectComment
        fields = ["project_id", "text"]


class ProjectCommentTextSerializer(serializers.ModelSerializer):
    """ Field that can only be interacted with"""

    class Meta:
        model = ProjectComment
        fields = ["text"]
