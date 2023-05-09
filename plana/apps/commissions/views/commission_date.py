"""Views linked to commissions dates."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.utils import to_bool


class CommissionDateList(generics.ListAPIView):
    """/commissions/commission_dates route"""

    permission_classes = [AllowAny]
    queryset = CommissionDate.objects.all().order_by("submission_date")
    serializer_class = CommissionDateSerializer

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
