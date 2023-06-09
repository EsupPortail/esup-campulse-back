"""List of URLs directly linked to operations that can be done on commissions."""
from django.urls import path

from .views.commission import CommissionList
from .views.commission_date import (
    CommissionDateListCreate,
    CommissionDateRetrieveUpdateDestroy,
)

urlpatterns = [
    path("", CommissionList.as_view(), name="commission_list"),
    path(
        "commission_dates",
        CommissionDateListCreate.as_view(),
        name="commission_date_list_create",
    ),
    path(
        "commission_dates/<int:pk>",
        CommissionDateRetrieveUpdateDestroy.as_view(),
        name="commission_date_retrieve_update_destroy",
    ),
]
