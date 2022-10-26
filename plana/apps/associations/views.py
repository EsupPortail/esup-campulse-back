from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import AssociationSerializer
from .models import Association


class AssociationView(APIView):
    serializer_class = AssociationSerializer

    def get(self, request):
        queryset = Association.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

# Create your views here.
#def index(self):
#    data = {"test associations": "test associations"}
#    return JsonResponse(data)

