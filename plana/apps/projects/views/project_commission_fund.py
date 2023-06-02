"""Views linked to project commission dates links."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.serializers.project_commission_fund import (
    ProjectCommissionFundDataSerializer,
    ProjectCommissionFundSerializer,
)


class ProjectCommissionFundListCreate(generics.ListCreateAPIView):
    """/projects/commission_dates route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundSerializer

    @extend_schema(
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
        responses={
            status.HTTP_200_OK: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["projects/commission_dates"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all commission dates that can be linked to a project."""
        project_id = request.query_params.get("project_id")
        commission_id = request.query_params.get("commission_id")

        if not request.user.has_perm(
            "projects.view_projectcommissiondate_any_commission"
        ):
            if request.user.is_staff:
                user_funds_ids = request.user.get_user_managed_funds()
            else:
                user_funds_ids = request.user.get_user_funds()
        else:
            user_funds_ids = Fund.objects.all().values_list("id")
        if not request.user.has_perm(
            "projects.view_projectcommissiondate_any_institution"
        ):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm(
            "projects.view_projectcommissiondate_any_commission"
        ) or not request.user.has_perm(
            "projects.view_projectcommissiondate_any_institution"
        ):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            self.queryset = self.queryset.filter(
                models.Q(project_id__in=user_projects_ids)
                | models.Q(
                    commission_date_id__in=Commission.objects.filter(
                        commission_id__in=user_funds_ids
                    ).values_list("id")
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

        if commission_id:
            commission_dates_ids = Commission.objects.filter(
                commission_id=commission_id
            ).values_list("id")
            self.queryset = self.queryset.filter(
                commission_date_id__in=commission_dates_ids
            )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: ProjectCommissionFundSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_dates"],
    )
    def post(self, request, *args, **kwargs):
        """Creates a link between a project and a commission date."""
        try:
            project = Project.visible_objects.get(id=request.data["project"])
            commission_date = Commission.objects.get(id=request.data["commission_date"])
            fund = Fund.objects.get(id=commission_date.commission_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project or commission date does not exist.")},
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

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        validator_fields = [
            "amount_earned",
            "is_validated_by_admin",
        ]
        if not request.user.has_perm(
            "project.change_projectcommissiondate_as_validator"
        ):
            for validator_field in validator_fields:
                if (
                    validator_field in request.data
                    and request.data[validator_field] is not None
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Not allowed to update validator fields for this project's commission."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        if fund.is_site is True and (
            project.user_id is not None
            or (
                project.association_id is not None
                and Association.objects.get(id=project.association_id).is_site is False
            )
        ):
            return response.Response(
                {"error": _("Not allowed to submit a project to this commission.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if commission_date.submission_date < datetime.date.today():
            return response.Response(
                {"error": _("Submission date for this commission is gone.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission_date_next = Commission.objects.filter(
            commission_id=commission_date.commission_id
        ).order_by("submission_date")[0]
        if commission_date != commission_date_next:
            return response.Response(
                {"error": _("Submissions are only available for the next commission.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commissions_with_project = Fund.objects.filter(
            id__in=Commission.objects.filter(
                id__in=ProjectCommissionFund.objects.filter(
                    project=request.data["project"]
                ).values_list("commission_date_id")
            ).values_list("commission_id")
        ).values_list("id", flat=True)
        if commission_date.commission_id in commissions_with_project:
            return response.Response(
                {"error": _("This project is already submitted for this commission.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.edition_date = datetime.date.today()
        project.save()

        return super().create(request, *args, **kwargs)


class ProjectCommissionFundRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/commission_dates route"""

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
        tags=["projects/commission_dates"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieves all commission dates linked to a project."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm(
                "projects.view_projectcommissiondate_any_commission"
            )
            and not request.user.has_perm(
                "projects.view_projectcommissiondate_any_institution"
            )
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project commission dates.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


class ProjectCommissionFundUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/commission_dates/{commission_date_id} route"""

    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundDataSerializer

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
            status.HTTP_200_OK: ProjectCommissionFundSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_dates"],
    )
    def patch(self, request, *args, **kwargs):
        """Updates details of a project linked to a commission date."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pcd = ProjectCommissionFund.objects.get(
                project_id=kwargs["project_id"],
                commission_date_id=kwargs["commission_date_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "error": _(
                        "Link between this project and commission does not exist."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(pcd.project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        bearer_fields = [
            "is_first_edition",
            "amount_asked_previous_edition",
            "amount_earned_previous_edition",
            "amount_asked",
            "commission_date_id",
            "project_id",
        ]
        if not request.user.has_perm("project.change_projectcommissiondate_as_bearer"):
            for bearer_field in bearer_fields:
                if (
                    bearer_field in request.data
                    and request.data[bearer_field] is not None
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Not allowed to update bearer fields for this project's commission."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        validator_fields = [
            "amount_earned",
            "is_validated_by_admin",
        ]
        if not request.user.has_perm(
            "project.change_projectcommissiondate_as_validator"
        ):
            for validator_field in validator_fields:
                if (
                    validator_field in request.data
                    and request.data[validator_field] is not None
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Not allowed to update validator fields for this project's commission."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        commission_date = Commission.objects.get(id=kwargs["commission_date_id"])
        if commission_date.submission_date < datetime.date.today():
            return response.Response(
                {"error": _("Submission date for this commission is gone.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for field in request.data:
            setattr(pcd, field, request.data[field])
        pcd.save()
        return response.Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_dates"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys details of a project linked to a commission date."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
            pcd = ProjectCommissionFund.objects.get(
                project_id=kwargs["project_id"],
                commission_date_id=kwargs["commission_date_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "error": _(
                        "Link between this project and commission does not exist."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(pcd.project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()
        pcd.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
