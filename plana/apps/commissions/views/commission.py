"""Views linked to commissions."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.serializers.commission import (
    CommissionSerializer,
    CommissionUpdateSerializer,
)
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.utils import to_bool


class CommissionListCreate(generics.ListCreateAPIView):
    """/commissions/ route"""

    queryset = Commission.objects.all().order_by("submission_date")
    serializer_class = CommissionSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "commission_dates",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by commission_date field (multiple).",
            ),
            OpenApiParameter(
                "is_site",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter by is_site field.",
            ),
            OpenApiParameter(
                "only_next",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get only chronologically first commission of each type",
            ),
            OpenApiParameter(
                "active_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commission_dates where projects reviews are still pending.",
            ),
            OpenApiParameter(
                "managed_commissions",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commission_dates managed by the current user.",
            ),
            OpenApiParameter(
                "managed_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commission_dates with projects managed by the current user.",
            ),
        ],
        responses={
            status.HTTP_200_OK: CommissionSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all commissions."""
        commission_dates = request.query_params.get("commission_dates")
        is_site = request.query_params.get("is_site")
        only_next = request.query_params.get("only_next")
        active_projects = request.query_params.get("active_projects")
        managed_commissions = request.query_params.get("managed_commissions")
        managed_projects = request.query_params.get("managed_projects")

        if commission_dates is not None and commission_dates != "":
            commission_dates = commission_dates.split(",")
            commission_dates = [
                datetime.datetime.strptime(commission_date, "%Y-%m-%d").date()
                for commission_date in commission_dates
                if commission_date != ""
                and isinstance(
                    datetime.datetime.strptime(commission_date, "%Y-%m-%d").date(),
                    datetime.date,
                )
            ]
            self.queryset = self.queryset.filter(commission_date__in=commission_dates)

        if is_site is not None and is_site != "":
            self.queryset = self.queryset.filter(
                id__in=Fund.objects.filter(is_site=to_bool(is_site)).values_list("id")
            )

        if only_next is not None and only_next != "" and to_bool(only_next) is True:
            first_commission_date = (
                Commission.objects.all()
                .order_by("commission_date")
                .first()
                .commission_date
            )
            self.queryset = self.queryset.filter(commission_date=first_commission_date)

        if active_projects is not None and active_projects != "":
            inactive_projects = Project.visible_objects.filter(
                project_status__in=Project.ProjectStatus.get_archived_project_statuses()
            )
            if to_bool(active_projects) is False:
                self.queryset = self.queryset.filter(
                    id__in=ProjectCommissionFund.objects.filter(
                        project_id__in=inactive_projects
                    ).values_list("commission_fund_id")
                )
            else:
                self.queryset = self.queryset.exclude(
                    id__in=ProjectCommissionFund.objects.filter(
                        project_id__in=inactive_projects
                    ).values_list("commission_fund_id")
                )

        if (
            managed_commissions is not None
            and managed_commissions != ""
            and not request.user.is_anonymous
        ):
            if to_bool(managed_commissions) is True:
                self.queryset = self.queryset.filter(
                    commission_id__in=request.user.get_user_managed_funds()
                )
            else:
                self.queryset = self.queryset.exclude(
                    commission_id__in=request.user.get_user_managed_funds()
                )

        if (
            managed_projects is not None
            and managed_projects != ""
            and not request.user.is_anonymous
        ):
            if to_bool(managed_projects) is True:
                self.queryset = self.queryset.filter(
                    id__in=ProjectCommissionFund.objects.filter(
                        project_id__in=Project.visible_objects.filter(
                            association_id__in=request.user.get_user_managed_associations()
                        ).values_list("id")
                    ).values_list("commission_fund_id")
                )
            else:
                self.queryset = self.queryset.exclude(
                    id__in=ProjectCommissionFund.objects.filter(
                        project_id__in=Project.visible_objects.filter(
                            association_id__in=request.user.get_user_managed_associations()
                        ).values_list("id")
                    ).values_list("commission_fund_id")
                )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: CommissionSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Creates a new commission (manager only)."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "submission_date" in request.data
            and datetime.datetime.strptime(
                request.data["submission_date"], "%Y-%m-%d"
            ).date()
            < datetime.date.today()
        ):
            return response.Response(
                {
                    "error": _(
                        "Cannot create commission date taking place before today."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "submission_date" in request.data
            and "commission_date" in request.data
            and datetime.datetime.strptime(request.data["submission_date"], "%Y-%m-%d")
            > datetime.datetime.strptime(request.data["commission_date"], "%Y-%m-%d")
        ):
            return response.Response(
                {"error": _("Can't set submission date after commission date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class CommissionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/commissions/{id} route"""

    queryset = Commission.objects.all().order_by("submission_date")
    serializer_class = CommissionSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
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
            status.HTTP_200_OK: CommissionSerializer,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a commission date with all its details."""
        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission Date does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        return self.retrieve(request, *args, **kwargs)

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
            status.HTTP_200_OK: CommissionSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates commission date details."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission Date does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            "submission_date" in request.data
            and datetime.datetime.strptime(
                request.data["submission_date"], "%Y-%m-%d"
            ).date()
            < datetime.date.today()
        ):
            return response.Response(
                {
                    "error": _(
                        "Cannot create commission date taking place before today."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "submission_date" in request.data
            and "commission_date" in request.data
            and datetime.datetime.strptime(request.data["submission_date"], "%Y-%m-%d")
            > datetime.datetime.strptime(request.data["commission_date"], "%Y-%m-%d")
        ):
            return response.Response(
                {"error": _("Can't set submission date after commission date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.partial_update(request, *args, **kwargs)

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
        try:
            commission_id = self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if commission_id.commission_date < datetime.date.today():
            return response.Response(
                {"error": _("Cannot delete commission taking place before today.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        projects_commission_fund_count = ProjectCommissionFund.objects.filter(
            commission_fund_id=commission_id.id,
            project_id__in=Project.visible_objects.exclude(
                project_status__in=Project.ProjectStatus.get_draft_project_statuses()
            ),
        ).count()
        if projects_commission_fund_count > 0:
            return response.Response(
                {"error": _("Cannot delete commission date with linked projects.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.destroy(request, *args, **kwargs)
