from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def index(self):
    data = {"test users": "test users"}
    return JsonResponse(data)

