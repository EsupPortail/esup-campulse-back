from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def index(self):
    data = {"test associations": "test associations"}
    return JsonResponse(data)

