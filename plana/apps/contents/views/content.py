"""Views directly linked to contents."""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import ContentSerializer


class ContentList(generics.ListAPIView):
    """/contents/ route"""

    permission_classes = [AllowAny]
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

    def get(self, request, *args, **kwargs):
        """Lists all contents."""
        return self.list(request, *args, **kwargs)
