"""Views linked to commissions."""
import datetime
import unicodedata

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund
from plana.apps.commissions.serializers.commission import (
    CommissionSerializer,
    CommissionUpdateSerializer,
)
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.utils import to_bool, valid_date_format


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
                "dates",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by commission_date field (multiple).",
            ),
            OpenApiParameter(
                "is_site",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commission by fund is_site setting.",
            ),
            OpenApiParameter(
                "is_open_to_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get only commissions with open projects submissions.",
            ),
            OpenApiParameter(
                "funds",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by linked funds.",
            ),
            OpenApiParameter(
                "active_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commission_dates where projects reviews are still pending.",
            ),
            OpenApiParameter(
                "managed_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commissions with projects managed by the current user.",
            ),
        ],
        responses={
            status.HTTP_200_OK: CommissionSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all commissions."""
        dates = request.query_params.get("dates")
        is_site = request.query_params.get("is_site")
        is_open_to_projects = request.query_params.get("is_open_to_projects")
        funds = request.query_params.get("funds")
        active_projects = request.query_params.get("active_projects")
        managed_projects = request.query_params.get("managed_projects")

        if dates is not None and dates != "":
            commission_dates = dates.split(",")
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
                id__in=CommissionFund.objects.filter(
                    fund_id__in=Fund.objects.filter(
                        is_site=to_bool(is_site)
                    ).values_list("id")
                ).values_list("commission_id")
            )

        if is_open_to_projects is not None and is_open_to_projects != "":
            self.queryset = self.queryset.filter(
                is_open_to_projects=to_bool(is_open_to_projects)
            )

        if funds is not None and funds != "":
            self.queryset = self.queryset.filter(
                id__in=CommissionFund.objects.filter(
                    fund_id__in=funds.split(",")
                ).values_list("commission_id")
            )

        if active_projects is not None and active_projects != "":
            commissions_ids_with_inactive_projects = CommissionFund.objects.filter(
                id__in=ProjectCommissionFund.objects.filter(
                    project_id__in=Project.visible_objects.filter(
                        project_status__in=Project.ProjectStatus.get_archived_project_statuses()
                    )
                ).values_list("commission_fund_id")
            ).values_list("commission_id")
            commissions_ids_with_active_projects = CommissionFund.objects.filter(
                id__in=ProjectCommissionFund.objects.filter(
                    project_id__in=Project.visible_objects.filter(
                        project_status__in=Project.ProjectStatus.get_archived_project_statuses()
                    )
                ).values_list("commission_fund_id")
            ).values_list("commission_id")
            if to_bool(active_projects) is False:
                self.queryset = self.queryset.filter(
                    id__in=commissions_ids_with_inactive_projects
                ).exclude(id__in=commissions_ids_with_active_projects)
            else:
                self.queryset = self.queryset.exclude(
                    id__in=commissions_ids_with_inactive_projects
                ).filter(id__in=commissions_ids_with_active_projects)

        if (
            managed_projects is not None
            and managed_projects != ""
            and not request.user.is_anonymous
        ):
            if to_bool(managed_projects) is True:
                self.queryset = self.queryset.filter(
                    models.Q(
                        id__in=CommissionFund.objects.filter(
                            fund_id__in=ProjectCommissionFund.objects.filter(
                                project_id__in=Project.visible_objects.filter(
                                    association_id__in=request.user.get_user_managed_associations()
                                ).values_list("id")
                            ).values_list("commission_fund_id")
                        ).values_list('commission_id')
                    )
                    | models.Q(
                        id__in=CommissionFund.objects.filter(
                            fund_id__in=request.user.get_user_managed_funds()
                        ).values_list('commission_id')
                    )
                )
            else:
                self.queryset = self.queryset.exclude(
                    models.Q(
                        id__in=CommissionFund.objects.filter(
                            fund_id__in=ProjectCommissionFund.objects.filter(
                                project_id__in=Project.visible_objects.filter(
                                    association_id__in=request.user.get_user_managed_associations()
                                ).values_list("id")
                            ).values_list("commission_fund_id")
                        ).values_list('commission_id')
                    )
                    | models.Q(
                        id__in=CommissionFund.objects.filter(
                            fund_id__in=request.user.get_user_managed_funds()
                        ).values_list('commission_id')
                    )
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

        #      if "name" not in request.data:
        #          return response.Response(
        #              {"error": _("Commission name not set.")},
        #              status=status.HTTP_400_BAD_REQUEST,
        #          )

        # Removes spaces, uppercase and accented characters to avoid similar commission names.
        new_commission_name = (
            unicodedata.normalize(
                "NFD", request.data["name"].strip().replace(" ", "").lower()
            )
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        commissions = Commission.objects.all()
        for commission in commissions:
            existing_commission_name = (
                unicodedata.normalize(
                    "NFD", commission.name.strip().replace(" ", "").lower()
                )
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            if new_commission_name == existing_commission_name:
                return response.Response(
                    {"error": _("Commission name already taken.")},
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
                {"error": _("Commission does not exist.")},
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
        # try:
        #     serializer = self.get_serializer(data=request.data)
        #     serializer.is_valid(raise_exception=True)
        # except ValidationError as error:
        #     return response.Response(
        #         {"error": error.detail},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            "name" in request.data
            and request.data["name"] != ""
            and request.data["name"] is not None
        ):
            new_commission_name = (
                unicodedata.normalize(
                    "NFD", request.data["name"].strip().replace(" ", "").lower()
                )
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            commissions = Commission.objects.all()
            for commission in commissions:
                existing_commission_name = (
                    unicodedata.normalize(
                        "NFD", commission.name.strip().replace(" ", "").lower()
                    )
                    .encode("ascii", "ignore")
                    .decode("utf-8")
                )
                if new_commission_name == existing_commission_name:
                    return response.Response(
                        {"error": _("Commission name already taken.")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        if (
            "submission_date" in request.data
            and request.data["submission_date"] is not None
            and valid_date_format(request.data["submission_date"])
        ):
            if (
                datetime.datetime.strptime(
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
                "commission_date" in request.data
                and request.data["commission_date"] is not None
                and valid_date_format(request.data["commission_date"])
            ):
                commission_date = datetime.datetime.strptime(
                    request.data["commission_date"], "%Y-%m-%d"
                ).date()
            else:
                commission_date = self.queryset.get(id=kwargs["pk"]).commission_date
            if (
                datetime.datetime.strptime(
                    request.data["submission_date"], "%Y-%m-%d"
                ).date()
                > commission_date
            ):
                return response.Response(
                    {"error": _("Can't set submission date after commission date.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if (
            "commission_date" in request.data
            and request.data["commission_date"] is not None
            and valid_date_format(request.data["commission_date"])
        ):
            if (
                "submission_date" in request.data
                and request.data["commission_date"] is not None
                and valid_date_format(request.data["submission_date"])
            ):
                submission_date = datetime.datetime.strptime(
                    request.data["submission_date"], "%Y-%m-%d"
                ).date()
            else:
                submission_date = self.queryset.get(id=kwargs["pk"]).submission_date
            if (
                submission_date
                > datetime.datetime.strptime(
                    request.data["commission_date"], "%Y-%m-%d"
                ).date()
            ):
                return response.Response(
                    {"error": _("Can't set commission date before submission date.")},
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
            commission = self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if commission.commission_date < datetime.date.today():
            return response.Response(
                {"error": _("Cannot delete commission taking place before today.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        projects_commission_fund_count = ProjectCommissionFund.objects.filter(
            commission_fund_id__in=CommissionFund.objects.filter(
                commission_id=commission.id
            ),
            project_id__in=Project.visible_objects.exclude(
                project_status__in=Project.ProjectStatus.get_unfinished_project_statuses()
            ),
        ).count()
        if projects_commission_fund_count > 0:
            return response.Response(
                {"error": _("Cannot delete commission date with linked projects.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.destroy(request, *args, **kwargs)
