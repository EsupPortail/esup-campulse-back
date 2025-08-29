"""Custom error handler views + Base views."""

from datetime import date

from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plana.apps.associations.models import Association
from plana.apps.commissions.models import Commission
from plana.apps.documents.models import Document
from plana.serializers import StatsSerializer


class StatsView(APIView):
    """
    Returns some useful stats such as :
    - number of public associations
    - next open commission date
    - last update date of association charter process documents.
    """
    permission_classes = [AllowAny]
    serializer_class = StatsSerializer

    def get(self, request):
        next_commission = Commission.objects.filter(
            is_open_to_projects=True, commission_date__gt=date.today()
        ).order_by('commission_date').first()
        last_charter = Document.objects.filter(
            process_type="CHARTER_ASSOCIATION"
        ).order_by("-edition_date").first()

        stats = {
            "association_count": Association.objects.filter(is_public=True).count(),
            "next_commission_date": next_commission.commission_date if next_commission else None,
            "last_charter_update": last_charter.edition_date.date() if last_charter else None,
        }
        serializer = self.serializer_class(stats)
        return Response(serializer.data)


def ok(request, *args, **kwargs):
    """200 handler."""
    data = {"detail": "OK (200)"}
    return JsonResponse(data, status=status.HTTP_200_OK)


def forbidden(request, exception, *args, **kwargs):
    """403 error handler."""
    data = {"error": "Forbidden (403)"}
    return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)


def not_found(request, exception, *args, **kwargs):
    """404 error handler."""
    data = {"error": "Not Found (404)"}
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
