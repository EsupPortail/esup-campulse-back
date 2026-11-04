"""Views linked to commissions."""

import datetime

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.filters import CommissionFilter
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.serializers.commission import (
    CommissionSerializer,
    CommissionUpdateSerializer, CommissionManageSerializer
)
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.pagination import BasePageNumberPagination


class CommissionList(generics.ListAPIView):
    """/commissions/ route."""

    queryset = Commission.objects.all().distinct().order_by("submission_date").prefetch_related("commissionfund_set__fund")
    serializer_class = CommissionSerializer
    filterset_class = CommissionFilter
    permission_classes = [AllowAny]
    pagination_class = BasePageNumberPagination


class CommissionManageListCreate(generics.ListCreateAPIView):
    """/commissions/manage/ route."""

    queryset = Commission.objects.all().distinct().order_by("submission_date").prefetch_related("commissionfund_set__fund")
    serializer_class = CommissionManageSerializer
    filterset_class = CommissionFilter
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = BasePageNumberPagination

    def get_queryset(self):
        """Custom queryset with annotations to retrieve some projects counts, only for commissions managed by user."""
        manager_funds = self.request.user.get_user_managed_funds().values_list("pk")
        member_funds = self.request.user.get_user_funds().values_list("pk")
        return self.queryset.filter(
            Q(commissionfund__fund_id__in=manager_funds) | Q(commissionfund__fund_id__in=member_funds)
        ).annotate_projects_counts()


class CommissionRetrieve(generics.RetrieveAPIView):
    """/commissions/{id} route."""

    queryset = Commission.objects.all().order_by("submission_date").prefetch_related("commissionfund_set__fund")
    serializer_class = CommissionSerializer
    permission_classes = [AllowAny]


class CommissionManageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/commissions/{id}/manage route."""

    queryset = Commission.objects.all().order_by("submission_date").prefetch_related("commissionfund_set__fund")
    serializer_class = CommissionManageSerializer
    http_method_names = ["get", "patch", "delete"]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = CommissionUpdateSerializer
        else:
            self.serializer_class = CommissionManageSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """Custom queryset with annotations to retrieve some projects counts"""
        manager_funds = self.request.user.get_user_managed_funds().values_list("pk")
        member_funds = self.request.user.get_user_funds().values_list("pk")
        return self.queryset.filter(
            Q(commissionfund__fund_id__in=manager_funds) | Q(commissionfund__fund_id__in=member_funds)
        ).annotate_projects_counts().distinct()

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
