from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project_commission_date import (
    ProjectCommissionDateDataSerializer,
    ProjectCommissionDateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "project_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Project id.",
            )
            #            OpenApiParameter(
            #                "commission_id",
            #                OpenApiTypes.NUMBER,
            #                OpenApiParameter.QUERY,
            #                description="Commission id.",
            #            )
        ]
    )
)
class ProjectCommissionDateListCreate(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectCommissionDateSerializer

    def get_queryset(self):
        queryset = ProjectCommissionDate.objects.all()
        if self.request.method == "GET":
            project_id = self.request.query_params.get("project_id")
            if project_id:
                queryset = queryset.filter(project_id=project_id)
        return queryset

    def post(self, request, *args, **kwargs):
        if 'amount_earned' in request.data and request.data["amount_earned"] != None:
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

        try:
            ProjectCommissionDate.objects.get(
                project_id=request.data["project"],
                commission_date_id=request.data["commission_date"],
            )
            return response.Response(
                {
                    "error": _(
                        "Link between this project and this commission date already exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
            return super().create(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class ProjectCommissionDateRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    queryset = ProjectCommissionDate.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = ProjectCommissionDateSerializer
        else:
            self.serializer_class = ProjectCommissionDateDataSerializer
        return super().get_serializer_class()

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        try:
            pcd = ProjectCommissionDate.objects.get(pk=kwargs["pk"])
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

        if "amount_earned" in request.data:
            return response.Response(
                {"error": _("Not allowed to update amount earned for this project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            pcd = ProjectCommissionDate.objects.get(pk=kwargs["pk"])
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

        return super().delete(request, *args, **kwargs)
