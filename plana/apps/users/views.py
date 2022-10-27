from allauth_cas.views import CASCallbackView, CASLoginView, CASLogoutView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .adapter import CASAdapter
from .models import User
from .serializers import UserSerializer


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


login = CASLoginView.adapter_view(CASAdapter)
callback = CASCallbackView.adapter_view(CASAdapter)
