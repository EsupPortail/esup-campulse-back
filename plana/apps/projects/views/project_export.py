from django.db import models
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import generics

from plana.apps.commissions.models import Commission, CommissionDate
from plana.apps.projects.models import Project, ProjectCommissionDate
from plana.apps.projects.serializers.project import ProjectSerializer
from plana.utils import generate_pdf


class ProjectDataExport(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        # print(kwargs)
        data = get_object_or_404(Project, id=kwargs['id']).__dict__
        # print(data)
        data["project_commission_dates"] = list(
            ProjectCommissionDate.objects.filter(project_id=data["id"]).values(
                'commission_date_id',
                'is_first_edition',
                'amount_asked_previous_edition',
                'amount_earned_previous_edition',
                'amount_asked',
                'amount_earned',
            )
        )
        #        data["project_commission_dates"] = list(
        #            ProjectCommissionDate.objects.filter(project_id=data["id"]).annotate(
        #                commisson_date=Subquery(CommissionDate.objects.filter(id=OuterRef('commission_date_id')).values('commission_date'), output_field=models.DateField()),
        #                commission_acronym=Subquery(CommissionDate.objects.filter(id=OuterRef('commission_date_id')).values('commission_id').annotate(commission_acronym=Subquery(Commission.objects.filter(id=OuterRef('commission_id')).values('acronym'), output_field=models.CharField())))).values(
        #                'commission_date_id',
        #                'commission_date',
        #                'is_first_edition',
        #                'amount_asked_previous_edition',
        #                'amount_earned_previous_edition',
        #                'amount_asked',
        #                'amount_earned',
        #            )
        #        )
        print(data["project_commission_dates"])
        data["commissions"] = list(
            CommissionDate.objects.filter(
                pk__in=[
                    pcd["commission_date_id"]
                    for pcd in data["project_commission_dates"]
                ]
            )
            .annotate(
                commission_acronym=Subquery(
                    Commission.objects.filter(id=OuterRef('commission_id')).values(
                        'acronym'
                    ),
                    output_field=models.CharField(),
                )
            )
            .values('commission_acronym', 'commission_date')
        )
        print(data["commissions"])
        # print(data)
        return generate_pdf(data, "project_summary", request.build_absolute_uri('/'))
