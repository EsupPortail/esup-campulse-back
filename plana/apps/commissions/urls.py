"""List of URLs directly linked to operations that can be done on commissions."""
from django.urls import path

from .views.commission import CommissionListCreate, CommissionRetrieveUpdateDestroy
from .views.commission_export import CommissionExport
from .views.commission_fund import (
    CommissionFundDestroy,
    CommissionFundListCreate,
    CommissionFundRetrieve,
)
from .views.fund import FundList

urlpatterns = [
    path("", CommissionListCreate.as_view(), name="commission_list_create"),
    path(
        "<int:pk>",
        CommissionRetrieveUpdateDestroy.as_view(),
        name="commission_retrieve_update_destroy",
    ),
    path(
        "<int:pk>/export",
        CommissionExport.as_view(),
        name="commission_export",
    ),
    path(
        "funds", CommissionFundListCreate.as_view(), name="commission_fund_list_create"
    ),
    path(
        "<int:commission_id>/funds",
        CommissionFundRetrieve.as_view(),
        name="commission_fund_retrieve",
    ),
    path(
        "<int:commission_id>/funds/<int:fund_id>",
        CommissionFundDestroy.as_view(),
        name="commission_fund_destroy",
    ),
    path("funds/names", FundList.as_view(), name="fund_list"),
]
