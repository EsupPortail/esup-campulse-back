"""List of URLs directly linked to operations that can be done on commissions."""
from django.urls import path

from .views.commission import CommissionList

urlpatterns = [
    path("", CommissionList.as_view(), name="commission_list"),
]
