"""Views linked to project commission dates links."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project_commission_date import (
    ProjectCommissionDateDataSerializer,
    ProjectCommissionDateSerializer,
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
                        commission_date_id__in=CommissionDate.objects.filter(
                            commission_id__in=user_commissions_ids
                        ).values_list("id")
                    )
                )

        return queryset

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
            status.HTTP_200_OK: ProjectCommissionDateSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["projects/commission_dates"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all commission dates that can be linked to a project."""
        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: ProjectCommissionDateSerializer,
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
            project = Project.objects.get(pk=request.data["project"])
            commission_date = CommissionDate.objects.get(
                pk=request.data["commission_date"]
            )
            commission = Commission.objects.get(pk=commission_date.commission_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project or commission date does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "amount_earned" in request.data
            and request.data["amount_earned"] is not None
        ) or (
            "is_validated_by_admin" in request.data
            and request.data["is_validated_by_admin"] is not None
        ):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to update amount earned or validation for this project's commission."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if commission.is_site is True and (
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

        commission_date_next = CommissionDate.objects.filter(
            commission_id=commission_date.commission_id
        ).order_by("submission_date")[0]
        if commission_date != commission_date_next:
            return response.Response(
                {"error": _("Submissions are only available for the next commission.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commissions_with_project = Commission.objects.filter(
            id__in=CommissionDate.objects.filter(
                id__in=ProjectCommissionDate.objects.filter(
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


class ProjectCommissionDateRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/commission_dates route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionDate.objects.all()
    serializer_class = ProjectCommissionDateSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCommissionDateSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_dates"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieves all commission dates linked to a project."""
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
            not request.user.has_perm(
                "projects.view_projectcommissiondate_any_commission"
            )
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
                {"error": _("Not allowed to retrieve this project commission dates.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


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
            status.HTTP_200_OK: ProjectCommissionDateDataSerializer,
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

        if not request.user.can_edit_project(pcd.project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "amount_earned" in request.data
            and request.data["amount_earned"] is not None
        ) or (
            "is_validated_by_admin" in request.data
            and request.data["is_validated_by_admin"] is not None
        ):
            return response.Response(
                {"error": _("Not allowed to update amount earned for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        commission_date = CommissionDate.objects.get(pk=kwargs["commission_date_id"])
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
            status.HTTP_204_NO_CONTENT: ProjectCommissionDateDataSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_dates"],
    )
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

        if not request.user.can_edit_project(pcd.project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()
        pcd.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
