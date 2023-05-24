"""Views directly linked to projects categories."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer


class ProjectCategoryListCreate(generics.ListCreateAPIView):
    """/projects/categories route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

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
            status.HTTP_200_OK: ProjectCategorySerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["projects/categories"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all links between categories and projects."""
        project_id = request.query_params.get("project_id")

        user_commissions_ids = []
        user_institutions_ids = []
        if not request.user.has_perm("projects.view_projectcategory_any_commission"):
            if request.user.is_staff:
                user_commissions_ids = request.user.get_user_managed_commissions()
            else:
                user_commissions_ids = request.user.get_user_commissions()
        if not request.user.has_perm("projects.view_projectcategory_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()

        if not request.user.has_perm(
            "projects.view_projectcategory_any_commission"
        ) or not request.user.has_perm("projects.view_projectcategory_any_institution"):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            self.queryset = self.queryset.filter(
                models.Q(project_id__in=user_projects_ids)
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
            status.HTTP_201_CREATED: ProjectCategorySerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/categories"],
    )
    def post(self, request, *args, **kwargs):
        """Creates a link between a category and a project."""
        try:
            project = Project.visible_objects.get(id=request.data["project"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update categories for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()

        try:
            ProjectCategory.objects.get(
                project_id=request.data["project"], category_id=request.data["category"]
            )
        except ObjectDoesNotExist:
            return super().create(request, *args, **kwargs)

        return response.Response({}, status=status.HTTP_200_OK)


class ProjectCategoryRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/categories route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCategorySerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/categories"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieves all categories linked to a project."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_projectcategory_any_commission")
            and not request.user.has_perm(
                "projects.view_projectcategory_any_institution"
            )
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project categories.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


class ProjectCategoryDestroy(generics.DestroyAPIView):
    """/projects/{project_id}/categories/{category_id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: ProjectCategorySerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/categories"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a link between project and category."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
            project_category = ProjectCategory.objects.get(
                project_id=kwargs["project_id"], category_id=kwargs["category_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update categories for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()
        project_category.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
