# """Views directly linked to projects."""
# from rest_framework import generics
#
# from plana.apps.projects.models.category import Project
# from plana.apps.projects.serializers.category import ProjectSerializer
#
#
# class ProjectList(generics.ListAPIView):
#    """Lists all Categories."""
#
#    serializer_class = ProjectSerializer
#
#    def get_queryset(self):
#        """GET : Lists all projects."""
#        return Project.objects.all().order_by("name")
