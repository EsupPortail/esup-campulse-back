"""Views linked to commissions."""

import datetime

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.filters import CommissionFilter
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.serializers.commission import (
    CommissionSerializer,
    CommissionUpdateSerializer
)
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund


class CommissionListCreate(generics.ListCreateAPIView):
    """/commissions/ route."""

    queryset = Commission.objects.all().distinct().order_by("submission_date")
    serializer_class = CommissionSerializer
    filterset_class = CommissionFilter

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()


class CommissionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/commissions/{id} route."""

    queryset = Commission.objects.all().order_by("submission_date")
    serializer_class = CommissionSerializer
    http_method_names = ["get", "patch", "delete"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = CommissionUpdateSerializer
        else:
            self.serializer_class = CommissionSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: CommissionSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def delete(self, request, *args, **kwargs):
        """Destroys an entire commission (manager only)."""
        commission = self.get_object()

        if commission.commission_date < datetime.date.today():
            return response.Response(
                {"error": _("Cannot delete commission taking place before today.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        projects_commission_funds = ProjectCommissionFund.objects.filter(
            commission_fund__commission=commission,
            project_id__in=Project.visible_objects.exclude(
                project_status__in=Project.ProjectStatus.get_unfinished_project_statuses()
            ),
        )
        if projects_commission_funds.exists():
            return response.Response(
                {"error": _("Cannot delete commission date with linked projects.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.destroy(request, *args, **kwargs)
