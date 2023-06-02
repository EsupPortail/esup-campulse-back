"""List of URLs directly linked to operations that can be done on commissions."""
from django.urls import path

from .views.commission import CommissionListCreate, CommissionRetrieveUpdateDestroy
from .views.fund import FundList

urlpatterns = [
    path("funds/", FundList.as_view(), name="fund_list"),
    path(
        "",
        CommissionListCreate.as_view(),
        name="commission_list_create",
    ),
    path(
        "commission_dates/<int:pk>",
        CommissionRetrieveUpdateDestroy.as_view(),
        name="commission_retrieve_update_destroy",
    ),
]
