"""Views linked to project commission funds links."""

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import Commission, CommissionFund, Fund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.serializers.project_commission_fund import (
    ProjectCommissionFundDataSerializer,
    ProjectCommissionFundSerializer,
)
from ..filters import ProjectCommissionFundFilter

from plana.decorators import capture_queries

DATE_FORMAT = "%d %B %Y"


@extend_schema(
    tags=["projects/commission_funds"],
)
@method_decorator(capture_queries(), name='dispatch')
class ProjectCommissionFundListCreate(generics.ListCreateAPIView):
    """/projects/commission_funds route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundSerializer
    filterset_class = ProjectCommissionFundFilter

    def get_queryset(self):
        request = self.request
        queryset = super().get_queryset()

        if not request.user.has_perm("projects.view_projectcommissionfund_any_fund"):
            managed_funds = request.user.get_user_managed_funds()
            if managed_funds.exists():
                user_funds_ids = managed_funds
            else:
                user_funds_ids = request.user.get_user_funds()
        else:
            user_funds_ids = Fund.objects.all().values_list("id")
        if not request.user.has_perm("projects.view_projectcommissionfund_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm("projects.view_projectcommissionfund_any_fund") or not request.user.has_perm(
            "projects.view_projectcommissionfund_any_institution"
        ):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk) | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            queryset = queryset.filter(
                models.Q(project_id__in=user_projects_ids)
                | models.Q(commission_fund__fund__id__in=user_funds_ids.values_list("id"))
                | models.Q(
                    project__in=(
                        Project.visible_objects.filter(
                            association__institution_id__in=user_institutions_ids.values_list("id"))
                    )
                )
            )
        return queryset

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: ProjectCommissionFundSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def post(self, request, *args, **kwargs):
        """Create a link between a project and a commission fund object."""
        try:
            project = Project.visible_objects.get(id=request.data["project"])
            commission_fund = CommissionFund.objects.get(id=request.data["commission_fund"])
            fund = Fund.objects.get(id=commission_fund.fund_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project or commission date does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        validator_fields = [
            "amount_earned",
            "is_validated_by_admin",
        ]
        if not request.user.has_perm("projects.change_projectcommissionfund_as_validator"):
            for validator_field in validator_fields:
                if validator_field in request.data and request.data[validator_field] is not None:
                    return response.Response(
                        {"error": _("Not allowed to update validator fields for this project's commission fund.")},
                        status=status.HTTP_403_FORBIDDEN,
                    )

        if fund.is_site and (
            project.user_id is not None
            or (
                project.association_id is not None
                and not Association.objects.get(id=project.association_id).is_site
            )
        ):
            return response.Response(
                {"error": _("Not allowed to submit a project to this commission.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        commission = Commission.objects.get(id=commission_fund.commission_id)

        if commission.submission_date < datetime.date.today():
            return response.Response(
                {"error": _("Submission date for this commission is gone.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not commission.is_open_to_projects:
            return response.Response(
                {"error": _("This commission is not accepting submissions for now.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pcf = ProjectCommissionFund.objects.filter(
            project_id=request.data["project"],
            commission_fund_id=request.data["commission_fund"],
        )
        if pcf.exists():
            return response.Response(
                {"error": _("This project is already submitted to this commission fund.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission_funds = CommissionFund.objects.filter(projectcommissionfund__project=project)
        for commission_fund in commission_funds:
            if commission_fund.commission_id != commission.id:
                return response.Response(
                    {"error": _("Cannot submit a project to multiple commissions.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        project.edition_date = datetime.date.today()
        project.save()

        return super().create(request, *args, **kwargs)


class ProjectCommissionFundRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/commission_funds route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all commission dates linked to a project."""
        project = get_object_or_404(Project.visible_objects, id=kwargs["project_id"])

        if (
            not request.user.has_perm("projects.view_projectcommissionfund_any_fund")
            and not request.user.has_perm("projects.view_projectcommissionfund_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project commission funds.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(self.queryset.filter(project_id=kwargs["project_id"]), many=True)
        return response.Response(serializer.data)


class ProjectCommissionFundUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/commission_funds/{commission_fund_id} route."""

    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundDataSerializer
    http_method_names = ["patch", "delete"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            project__in=Project.visible_objects.all(),
            project_id=self.kwargs["project_id"],
            commission_fund_id=self.kwargs["commission_fund_id"],
        )

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCommissionFundDataSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def patch(self, request, *args, **kwargs):
        """Update details of a project linked to a commission fund object."""
        pcf = self.get_object()

        if not request.user.can_edit_project(pcf.project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return response.Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys details of a project linked to a commission date."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
            project_commission_fund = ProjectCommissionFund.objects.get(
                project_id=kwargs["project_id"],
                commission_fund_id=kwargs["commission_fund_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Link between this project and commission does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()
        project_commission_fund.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
