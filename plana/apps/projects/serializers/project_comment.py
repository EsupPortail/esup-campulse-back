"""Serializer describing fields used on project's comments"""
import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.users.serializers.user import UserNameSerializer
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class ProjectCommentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.visible_objects.all())
    user = UserNameSerializer()

    class Meta:
        model = ProjectComment
        fields = "__all__"


class ProjectCommentDataSerializer(serializers.ModelSerializer):
    """Used to post a comment for a project"""

    class Meta:
        model = ProjectComment
        fields = ["is_visible", "text"]
        # To specifically keep default=True behavior from model
        extra_kwargs = {"is_visible": {"default": True}}

    def validate(self, data):
        """Custom validate for project comments, the project must be in a status that authorizes comments"""
        view = self.context.get("view")
        project = get_object_or_404(Project.visible_objects.all(), pk=view.kwargs.get("project_id"))

        if project.project_status not in Project.ProjectStatus.get_commentable_project_statuses():
            raise serializers.ValidationError({"project_status": _("Cannot manage comments on a validated project/review.")})

        data["project"] = project
        return data

    def create(self, validated_data):
        """
        Custom create for project comments, auto-setup user with the one executing the request and sends email if needed
        """
        request = self.context.get("request")
        validated_data["user"] = request.user

        comment = super().create(validated_data)

        if comment.is_visible:
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
            }
            template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_COMMENT")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=validated_data["project"].get_project_owner_data().get("email"),
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )
        return comment


class ProjectCommentUpdateSerializer(serializers.ModelSerializer):
    """Fields that can be updated."""

    def update(self, instance, validated_data):
        instance.edition_date = datetime.date.today()
        return super().update(instance, validated_data)

    class Meta:
        model = ProjectComment
        fields = ["text", "is_visible"]
