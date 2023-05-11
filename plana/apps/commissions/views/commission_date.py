"""Views linked to commissions dates."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission_date import (
    CommissionDateSerializer,
    CommissionDateUpdateSerializer,
)
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.utils import to_bool


class CommissionDateListCreate(generics.ListCreateAPIView):
    """/commissions/commission_dates route"""

    queryset = CommissionDate.objects.all().order_by("submission_date")
    serializer_class = CommissionDateSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    @extend_schema(
        parameters=[
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
                "managed_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get commission_dates with projects managed by the current user.",
            ),
        ],
        responses={
            status.HTTP_200_OK: CommissionDateSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all commission dates."""
        only_next = request.query_params.get("only_next")
        active_projects = request.query_params.get("active_projects")
        managed_projects = request.query_params.get("managed_projects")

        if only_next is not None and only_next != "" and to_bool(only_next) is True:
            first_commissions_ids = []
            commissions = Commission.objects.all().values_list("id")
            for commission_id in commissions:
                first_commissions_ids.append(
                    CommissionDate.objects.filter(commission_id=commission_id)
                    .order_by("submission_date")
                    .first()
                    .id
                )
            self.queryset = self.queryset.filter(id__in=first_commissions_ids)

        if active_projects is not None and active_projects != "":
            inactive_projects = Project.objects.filter(
                project_status__in=Project.ProjectStatus.get_archived_project_statuses()
            )
            if to_bool(active_projects) is False:
                self.queryset = self.queryset.filter(
                    id__in=ProjectCommissionDate.objects.filter(
                        project_id__in=inactive_projects
                    ).values_list("commission_date_id")
                )
            else:
                self.queryset = self.queryset.exclude(
                    id__in=ProjectCommissionDate.objects.filter(
                        project_id__in=inactive_projects
                    ).values_list("commission_date_id")
                )

        if (
            managed_projects is not None
            and managed_projects != ""
            and not request.user.is_anonymous
        ):
            if to_bool(managed_projects) is True:
                self.queryset = self.queryset.filter(
                    id__in=ProjectCommissionDate.objects.filter(
                        project_id__in=Project.objects.filter(
                            association_id__in=request.user.get_user_managed_associations()
                        ).values_list("id")
                    ).values_list("commission_date_id")
                )
            else:
                self.queryset = self.queryset.exclude(
                    id__in=ProjectCommissionDate.objects.filter(
                        project_id__in=Project.objects.filter(
                            association_id__in=request.user.get_user_managed_associations()
                        ).values_list("id")
                    ).values_list("commission_date_id")
                )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: CommissionDateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Creates a new commission date (manager only)."""
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


class CommissionDateRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/commissions/commission_dates/{id} route"""

    queryset = CommissionDate.objects.all().order_by("submission_date")
    serializer_class = CommissionDateSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = CommissionDateUpdateSerializer
        else:
            self.serializer_class = CommissionDateSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: CommissionDateSerializer,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a document type with all its details."""
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
            status.HTTP_200_OK: CommissionDateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates commission date details."""
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
            status.HTTP_204_NO_CONTENT: CommissionDateSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def delete(self, request, *args, **kwargs):
        """Destroys an entire commission date (manager only)."""
        try:
            commission_date = self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission Date does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if commission_date.commission_date < datetime.date.today():
            return response.Response(
                {
                    "error": _(
                        "Cannot delete commission date taking place before today."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.destroy(request, *args, **kwargs)
