from django.shortcuts import render, get_object_or_404

from rest_framework import generics, status

from .serializers import UserSerializer
from .models import User

# Create your views here.
#def index(self):
#    data = {"test users": "test users"}
#    return JsonResponse(data)

class UserList(generics.ListCreateAPIView):
    """
    Generic DRF view to list associations or create a new one
    GET: list
    POST: create
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().order_by('username')


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET a single association (pk)
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
