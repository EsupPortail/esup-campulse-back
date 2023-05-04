from django.db import models
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import generics

from plana.apps.associations.models import Association
from plana.apps.commissions.models import Commission, CommissionDate
from plana.apps.projects.models import Project, ProjectCommissionDate
from plana.apps.projects.serializers.project import ProjectSerializer
from plana.utils import generate_pdf


class ProjectDataExport(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        # TODO : Fill user "other" data when indivudual project
        data = get_object_or_404(Project, id=kwargs['id']).__dict__

        if data["association_id"] is not None:
            data["association"] = Association.objects.get(
                id=data["association_id"]
            ).name

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
        commission_infos = list(
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
            .values('commission_acronym', 'commission_date', 'id')
        )
        for commission in commission_infos:
            for link in data['project_commission_dates']:
                if commission['id'] == link['commission_date_id']:
                    link["commission_acronym"] = commission["commission_acronym"]
                    link["commission_date"] = commission["commission_date"]

        data["is_first_edition"] = True
        for edition in data["project_commission_dates"]:
            if not edition["is_first_edition"]:
                data["is_first_edition"] = False
                break
        print(data)
        return generate_pdf(data, "project_summary", request.build_absolute_uri('/'))
