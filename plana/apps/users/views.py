from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer
from .models import User


class UserView(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

# Create your views here.
#def index(self):
#    data = {"test users": "test users"}
#    return JsonResponse(data)

