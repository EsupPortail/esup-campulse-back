"""Views directly linked to projects categories."""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.permissions import ProjectCategoryUpdatePermission
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer


@extend_schema(tags=["projects/categories"])
class ProjectCategoryListCreate(generics.ListCreateAPIView):
    """/projects/categories route."""

    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), DjangoModelPermissions(), ProjectCategoryUpdatePermission()]
        return [IsAuthenticated(), DjangoModelPermissions()]

    # FIXME : If permission to get some projects data, also have permission to retrieve their linked categories (custom manager)
    def get(self, request, *args, **kwargs):
        """List all links between categories and projects."""
        project_id = request.query_params.get("project_id")

        user_funds_ids = []
        user_institutions_ids = []
        if not request.user.has_perm("projects.view_projectcategory_any_fund"):
            managed_funds = request.user.get_user_managed_funds()
            if managed_funds.exists():
                user_funds_ids = managed_funds
            else:
                user_funds_ids = request.user.get_user_funds()
        if not request.user.has_perm("projects.view_projectcategory_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()

        if not request.user.has_perm("projects.view_projectcategory_any_fund") or not request.user.has_perm(
            "projects.view_projectcategory_any_institution"
        ):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk) | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            self.queryset = self.queryset.filter(
                models.Q(project_id__in=user_projects_ids)
                | models.Q(project__projectcommissionfund__commission_fund__fund_id__in=user_funds_ids.values_list("id"))
                | models.Q(project__in=(Project.visible_objects.filter(association__institution__in=user_institutions_ids.values_list("id"))))
            )

        if project_id:
            self.queryset = self.queryset.filter(project_id=project_id)

        return self.list(request, *args, **kwargs)


# TODO : Still useful ?
class ProjectCategoryRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/categories route."""

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
        """Retrieve all categories linked to a project."""
        project = get_object_or_404(Project.visible_objects, id=kwargs["project_id"])

        if (
            not request.user.has_perm("projects.view_projectcategory_any_fund")
            and not request.user.has_perm("projects.view_projectcategory_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project categories.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(self.queryset.filter(project_id=kwargs["project_id"]), many=True)
        return response.Response(serializer.data)


@extend_schema(tags=["projects/categories"])
class ProjectCategoryDestroy(generics.DestroyAPIView):
    """/projects/{project_id}/categories/{category_id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions, ProjectCategoryUpdatePermission]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            project_id=self.kwargs["project_id"],
            category_id=self.kwargs["category_id"]
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_destroy(self, instance):
        """ProjectCategory object deletion should update the Project's edition date"""
        instance.project.edition_date = timezone.now()
        instance.project.save()
        instance.delete()
