from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer
from .models import User


class UserView(APIView):
    serializer_class = UserSerializer

    def get(self, request, pk=None):
        if pk:
            queryset = get_object_or_404(User, pk=pk)
            many = False
        else:
            queryset = User.objects.all()
            many = True

        serializer = self.serializer_class(queryset, many=many)
        return Response(serializer.data)

# Create your views here.
#def index(self):
#    data = {"test users": "test users"}
#    return JsonResponse(data)

