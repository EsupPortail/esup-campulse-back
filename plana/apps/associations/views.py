from django.shortcuts import render, get_object_or_404

from rest_framework import generics, status

from .serializers import AssociationSerializer
from .models import Association


class AssociationList(generics.ListCreateAPIView):
    """
    Generic DRF view to list associations or create a new one
    GET: list
    POST: create
    """
    serializer_class = AssociationSerializer

    def get_queryset(self):
        return Association.objects.filter(is_enabled=True).order_by('name')


class AssociationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET a single association (pk)
    """
    serializer_class = AssociationSerializer
    queryset = Association.objects.all()

