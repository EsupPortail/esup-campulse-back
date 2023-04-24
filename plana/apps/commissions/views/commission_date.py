"""Views linked to commissions dates."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.utils import to_bool


@extend_schema_view(
    get=extend_schema(
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
        ]
    )
)
class CommissionDateList(generics.ListAPIView):
    """/commissions/commission_dates route"""

    permission_classes = [AllowAny]
    serializer_class = CommissionDateSerializer

    def get_queryset(self):
        queryset = CommissionDate.objects.all().order_by("submission_date")
        if self.request.method == "GET":
            only_next = self.request.query_params.get("only_next")
            active_projects = self.request.query_params.get("active_projects")
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
                queryset = queryset.filter(id__in=first_commissions_ids)
            if active_projects is not None and active_projects != "":
                inactive_projects = Project.objects.filter(
                    project_status__in=[
                        "PROJECT_DRAFT",
                        "PROJECT_REJECTED",
                        "PROJECT_REVIEW_CANCELLED",
                        "PROJECT_REVIEW_VALIDATED",
                    ]
                )
                if to_bool(active_projects) is False:
                    queryset = queryset.filter(
                        id__in=ProjectCommissionDate.objects.filter(
                            project_id__in=inactive_projects
                        ).values_list("commission_date_id")
                    )
                else:
                    queryset = queryset.exclude(
                        id__in=ProjectCommissionDate.objects.filter(
                            project_id__in=inactive_projects
                        ).values_list("commission_date_id")
                    )

        return queryset

    def get(self, request, *args, **kwargs):
        """Lists all commission dates."""
        return self.list(request, *args, **kwargs)
