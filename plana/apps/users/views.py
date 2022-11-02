from allauth_cas.views import CASCallbackView, CASLoginView, CASLogoutView
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status

from .adapter import CASAdapter
from .models import User
from .serializers import UserSerializer


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

login = CASLoginView.adapter_view(CASAdapter)
callback = CASCallbackView.adapter_view(CASAdapter)

