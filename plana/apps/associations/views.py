from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import AssociationSerializer
from .models import Association


class AssociationView(APIView):
    serializer_class = AssociationSerializer

    def get(self, request, pk=None):
        if pk:
            queryset = get_object_or_404(Association, pk=pk)
            many = False
        else:
            queryset = Association.objects.all()
            many = True
        serializer = self.serializer_class(queryset, many=many)
        return Response(serializer.data)

# Create your views here.
#def index(self):
#    data = {"test associations": "test associations"}
#    return JsonResponse(data)

