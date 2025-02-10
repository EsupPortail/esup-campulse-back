"""Views directly linked to projects comments."""

import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.serializers.project_comment import (
    ProjectCommentDataSerializer,
    ProjectCommentSerializer,
    ProjectCommentUpdateSerializer,
)
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


class ProjectCommentCreate(generics.CreateAPIView):
    """/projects/comments route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentDataSerializer

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: ProjectCommentSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/comments"],
    )
    def post(self, request, *args, **kwargs):
        """Create a link between a comment and a project."""

        project = get_object_or_404(Project.visible_objects.all(), id=request.data["project"])
        request.data["user"] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        if project.project_status not in Project.ProjectStatus.get_commentable_project_statuses():
            return response.Response(
                {"error": _("Cannot manage comments on a validated project/review.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = datetime.date.today()
        request.data["creation_date"] = today
        request.data["edition_date"] = today
        request.data["user"] = request.user.pk

        if "is_visible" not in request.data or (
            request.data["is_visible"] != "" and to_bool(request.data["is_visible"]) is True
        ):
            current_site = get_current_site(request)
            context = {
                "site_domain": f"https://{current_site.domain}",
                "site_name": current_site.name,
            }
            template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_COMMENT")
            email = None
            if project.association_id is not None:
                if project.association_user_id is not None:
                    email = User.objects.get(
                        id=AssociationUser.objects.get(id=project.association_user_id).user_id
                    ).email
                else:
                    email = Association.objects.get(id=project.association_id).email
            elif project.user_id is not None:
                email = User.objects.get(id=project.user_id).email
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        return super().create(request, *args, **kwargs)


class ProjectCommentRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/comments route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCommentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/comments"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all comments linked to a project."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
        except Project.DoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_projectcomment_any_fund")
            and not request.user.has_perm("projects.view_projectcomment_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve these project comments.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.has_perm("projects.view_projectcomment_not_visible"):
            serializer = self.serializer_class(
                self.queryset.filter(project_id=kwargs["project_id"], is_visible=True),
                many=True,
            )
        else:
            serializer = self.serializer_class(self.queryset.filter(project_id=kwargs["project_id"]), many=True)

        return response.Response(serializer.data)


class ProjectCommentUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/comments/{pk} route."""

    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentUpdateSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    http_method_names = ["patch", "delete"]

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCommentSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/comments"],
    )
    def patch(self, request, *args, **kwargs):
        """Update comments of the project."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_comment = get_object_or_404(
            self.get_queryset(),
            project_id=kwargs["project_id"],
            id=kwargs["pk"]
        )
        project = get_object_or_404(Project.visible_objects.all(), id=kwargs["project_id"])

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.project_status not in Project.ProjectStatus.get_commentable_project_statuses():
            return response.Response(
                {"error": _("Cannot manage comments on a validated project/review.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_comment.edition_date = datetime.date.today()
        project_comment.text = request.data["text"]
        project_comment.is_visible = request.data["is_visible"]
        project_comment.save()
        return response.Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: ProjectCommentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/comments"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys comments of a project."""

        project_comment = get_object_or_404(
            self.get_queryset(),
            project_id=kwargs["project_id"],
            id=kwargs["pk"]
        )
        project = get_object_or_404(Project.visible_objects.all(), id=kwargs["project_id"])

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.project_status not in Project.ProjectStatus.get_commentable_project_statuses():
            return response.Response(
                {"error": _("Cannot manage comments on a validated project/review.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_comment.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
