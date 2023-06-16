"""Views directly linked to commission exports."""
import csv

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.projects.models import Project
from plana.apps.projects.serializers.project import ProjectSerializer


class CommissionProjectsCSVExport(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        """Projects presented to the commission CSV export."""
        commission = kwargs["pk"]

        http_response = HttpResponse(content_type="application/csv")
        http_response[
            "Content-Disposition"
        ] = f"Content-Disposition: attachment; filename='commission_{commission}_export.csv'"

        writer = csv.writer(http_response)
        # Write column titles for the CSV file
        writer.writerow(
            [
                _("Project ID"),
                _("Association name"),
                _("Student misc name"),
                _("Commission date"),
                _("Start Date"),
                _("End Date"),
                _("Reedition"),
                _("Categories"),
            ]
        )
        # Add amount asked and earned for each fund

        #        # Write CSV file content
        #            writer.writerow(
        #                [
        #                ]
        #            )

        return http_response
