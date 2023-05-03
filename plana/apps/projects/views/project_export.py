from django.shortcuts import get_object_or_404
from rest_framework import generics

from plana.apps.projects.models import Project
from plana.apps.projects.serializers.project import ProjectSerializer
from plana.utils import generate_pdf


class ProjectDataExport(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        print(request.data)
        print(kwargs)
        project = get_object_or_404(Project, id=kwargs['id'])
        return generate_pdf(
            project.__dict__, "project", request.build_absolute_uri('/')
        )
