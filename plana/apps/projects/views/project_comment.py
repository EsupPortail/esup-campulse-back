"""Views directly linked to projects comments."""
import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import Commission, CommissionDate
from plana.apps.institutions.models import Institution
from plana.apps.projects.models import ProjectCommissionDate
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.serializers.project_comment import (
    ProjectCommentDataSerializer,
    ProjectCommentSerializer,
    ProjectCommentTextSerializer,
)
from plana.apps.users.models.user import User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class ProjectCommentListCreate(generics.ListCreateAPIView):
    """/projects/comments route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectComment.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = ProjectCommentDataSerializer
        else:
            self.serializer_class = ProjectCommentSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "project_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Project id.",
            ),
        ],
        responses={
            status.HTTP_200_OK: ProjectCommentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["projects/comments"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all links between projects and comments"""

        project_id = request.query_params.get("project_id")

        if not request.user.has_perm("projects.view_projectcomment_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm("projects.view_projectcomment_any_commission"):
            if request.user.is_staff:
                user_commissions_ids = request.user.get_user_managed_commissions()
            else:
                user_commissions_ids = request.user.get_user_commissions()
        else:
            user_commissions_ids = Commission.objects.all().values_list("id")

        if not request.user.has_perm(
            "projects.view_projectcomment_any_commission"
        ) or not request.user.has_perm("projects.view_projectcomment_any_institution"):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            self.queryset = self.queryset.filter(
                models.Q(id__in=user_projects_ids)
                | models.Q(
                    project_id__in=(
                        ProjectCommissionDate.objects.filter(
                            commission_date_id__in=CommissionDate.objects.filter(
                                commission_id__in=user_commissions_ids
                            ).values_list("id")
                        ).values_list("project_id")
                    )
                )
                | models.Q(
                    project_id__in=(
                        Project.visible_objects.filter(
                            association_id__in=Association.objects.filter(
                                institution_id__in=user_institutions_ids
                            ).values_list("id")
                        ).values_list("id")
                    )
                )
            )

        if project_id:
            self.queryset = self.queryset.filter(project_id=project_id)

        return self.list(request, *args, **kwargs)

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
        """Create a link between a comment and a project"""
        try:
            project = Project.visible_objects.get(id=request.data["project"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["creation_date"] = datetime.date.today()
        request.data["edition_date"] = datetime.date.today()
        request.data["user"] = request.user.pk

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
        }
        template = MailTemplate.objects.get(code="NEW_PROJECT_COMMENT")
        email = None
        if project.association_id is not None:
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
    """/projects/{project_id}/comments route"""

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
        """Retrieves all comments linked to a project"""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_projectcomment_any_commission")
            and not request.user.has_perm(
                "projects.view_projectcomment_any_institution"
            )
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve these project comments.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


class ProjectCommentUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/comments/{comment_id} route"""

    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentTextSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def get(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        """Updates comments of the project"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
            pc = ProjectComment.objects.get(
                project_id=kwargs["project_id"], id=kwargs["comment_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Link between this comment and project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        pc.edition_date = datetime.date.today()
        pc.save()
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
        """Destroys comments of a project"""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
            pc = ProjectComment.objects.get(
                project_id=kwargs["project_id"], id=kwargs["comment_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": "Link between this comment and project does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        pc.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
