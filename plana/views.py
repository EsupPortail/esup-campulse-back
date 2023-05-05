"""Custom error handler views."""
from django.http import JsonResponse
from rest_framework import status


def ok(request, *args, **kwargs):
    """
    Generic 200 handler.
    """
    data = {"detail": "OK (200)"}
    return JsonResponse(data, status=status.HTTP_200_OK)


def forbidden(request, exception, *args, **kwargs):
    """
    Generic 403 error handler.
    """
    data = {"error": "Forbidden (403)"}
    return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)


def not_found(request, exception, *args, **kwargs):
    """
    Generic 404 error handler.
    """
    data = {"error": "Not Found (404)"}
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
