"""Views linked to project commission dates links."""

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project_commission_date import (
    ProjectCommissionDateDataSerializer,
    ProjectCommissionDateSerializer,
)
from plana.apps.users.models.user import AssociationUsers


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "project_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Project id.",
            ),
            OpenApiParameter(
                "commission_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Commission id.",
            ),
        ],
        tags=["projects/commission_dates"],
    ),
    post=extend_schema(tags=["projects/commission_dates"]),
)
class ProjectCommissionDateListCreate(generics.ListCreateAPIView):
    """/projects/commission_dates route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ProjectCommissionDateSerializer

    def get_queryset(self):
        queryset = ProjectCommissionDate.objects.all()
        if self.request.method == "GET":
            project_id = self.request.query_params.get("project_id")
            commission_id = self.request.query_params.get("commission_id")
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            if commission_id:
                commission_dates_ids = CommissionDate.objects.filter(
                    commission_id=commission_id
                ).values_list("id")
                queryset = queryset.filter(commission_date_id__in=commission_dates_ids)

            if not self.request.user.has_perm(
                "projects.view_projectcommissiondate_all"
            ):
                user_associations_ids = AssociationUsers.objects.filter(
                    user_id=self.request.user.pk
                ).values_list("association_id")
                user_projects_ids = Project.objects.filter(
                    Q(user_id=self.request.user.pk)
                    | Q(association_id__in=user_associations_ids)
                ).values_list("id")
                queryset = queryset.filter(project_id__in=user_projects_ids)

        return queryset

    def get(self, request, *args, **kwargs):
        """Lists all commission dates that can be linked to a project."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a link between a project and a commission date."""
        if (
            "amount_earned" in request.data
            and request.data["amount_earned"] is not None
        ):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to update amount earned for this project's commission."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(pk=request.data["project"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.now()
        project.save()

        try:
            ProjectCommissionDate.objects.get(
                project_id=request.data["project"],
                commission_date_id=request.data["commission_date"],
            )
        except ObjectDoesNotExist:
            return super().create(request, *args, **kwargs)

        return response.Response({}, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(tags=["projects/commission_dates"]),
)
class ProjectCommissionDateRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/commission_dates route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionDate.objects.all()
    serializer_class = ProjectCommissionDateSerializer

    def get(self, request, *args, **kwargs):
        """Retrieves all commission dates linked to a project."""
        try:
            project = Project.objects.get(id=kwargs["project_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No project found for this ID.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm(
            "projects.view_projectcommissiondate_all"
        ) and not project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to retrieve this project commission dates.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


@extend_schema(methods=["GET", "PUT"], exclude=True)
@extend_schema_view(
    patch=extend_schema(tags=["projects/commission_dates"]),
    delete=extend_schema(tags=["projects/commission_dates"]),
)
class ProjectCommissionDateUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/commission_dates/{commission_date_id} route"""

    queryset = ProjectCommissionDate.objects.all()
    serializer_class = ProjectCommissionDateDataSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        """Updates details of a project linked to a commission date."""
        try:
            pcd = ProjectCommissionDate.objects.get(
                project_id=kwargs["project_id"],
                commission_date_id=kwargs["commission_date_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "error": _(
                        "Link between this project and commission does not exists."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm(
            "projects.change_projectcommissiondate_basic_fields"
        ):
            return response.Response(
                {"error": _("Not allowed to update basic fields for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not pcd.project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "amount_earned" in request.data:
            return response.Response(
                {"error": _("Not allowed to update amount earned for this project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for field in request.data:
            setattr(pcd, field, request.data[field])
        pcd.save()
        return response.Response({}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """Destroys details of a project linked to a commission date."""
        try:
            project = Project.objects.get(pk=kwargs["project_id"])
            pcd = ProjectCommissionDate.objects.get(
                project_id=kwargs["project_id"],
                commission_date_id=kwargs["commission_date_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "error": _(
                        "Link between this project and commission does not exists."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not pcd.project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.now()
        project.save()
        pcd.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
