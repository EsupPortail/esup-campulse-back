"""Views directly linked to projects categories."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer
from plana.apps.users.models.user import AssociationUser


@extend_schema_view(
    get=extend_schema(tags=["projects/categories"]),
    post=extend_schema(tags=["projects/categories"]),
)
class ProjectCategoryListCreate(generics.ListCreateAPIView):
    """/projects/categories route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ProjectCategorySerializer

    def get_queryset(self):
        queryset = ProjectCategory.objects.all()
        if self.request.method == "GET":
            project_id = self.request.query_params.get("project_id")
            if project_id:
                queryset = queryset.filter(project_id=project_id)

            if not self.request.user.has_perm(
                "projects.view_projectcommissiondate_any_commission"
            ):
                user_associations_ids = self.request.user.get_user_associations()
                user_commissions_ids = self.request.user.get_user_commissions()
                user_projects_ids = Project.objects.filter(
                    models.Q(user_id=self.request.user.pk)
                    | models.Q(association_id__in=user_associations_ids)
                ).values_list("id")
                queryset = queryset.filter(
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
                )

        return queryset

    def get(self, request, *args, **kwargs):
        """Lists all links between categories and projects."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a link between a category and a project."""
        try:
            project = Project.objects.get(pk=request.data["project"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
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


@extend_schema_view(
    get=extend_schema(tags=["projects/categories"]),
)
class ProjectCategoryRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/categories route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    def get(self, request, *args, **kwargs):
        """Retrieves all categories linked to a project."""
        try:
            project = Project.objects.get(id=kwargs["project_id"])
            commissions_ids = CommissionDate.objects.filter(
                id__in=ProjectCommissionDate.objects.filter(
                    project_id=project.id
                ).values_list("commission_date_id")
            ).values_list("commission_id")
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_projectcategory_any_commission")
            and not request.user.can_edit_project(project)
            and (
                len(
                    list(
                        set(commissions_ids) & set(request.user.get_user_commissions())
                    )
                )
                == 0
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project categories.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


@extend_schema_view(
    delete=extend_schema(tags=["projects/categories"]),
)
class ProjectCategoryDestroy(generics.DestroyAPIView):
    """/projects/{project_id}/categories/{category_id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    def delete(self, request, *args, **kwargs):
        """Destroys a link between project and category."""
        try:
            project = Project.objects.get(pk=kwargs["project_id"])
            project_category = ProjectCategory.objects.get(
                project_id=kwargs["project_id"], category_id=kwargs["category_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update categories for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()
        project_category.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
