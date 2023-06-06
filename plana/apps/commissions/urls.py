"""List of URLs directly linked to operations that can be done on commissions."""
from django.urls import path

from .views.commission import CommissionListCreate, CommissionRetrieveUpdateDestroy
from .views.commission_fund import CommissionFundDestroy, CommissionFundListCreate
from .views.fund import FundList

urlpatterns = [
    path("funds/", FundList.as_view(), name="fund_list"),
    path(
        "commission_funds/",
        CommissionFundListCreate.as_view(),
        name="commission_fund_list_create",
    ),
    path(
        "commission_funds/<int:pk>",
        CommissionFundDestroy.as_view(),
        name="commission_fund_destroy",
    ),
    path(
        "",
        CommissionListCreate.as_view(),
        name="commission_list_create",
    ),
    path(
        "<int:pk>",
        CommissionRetrieveUpdateDestroy.as_view(),
        name="commission_retrieve_update_destroy",
    ),
]
