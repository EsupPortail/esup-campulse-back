"""List of URLs directly linked to operations that can be done on projects."""
from django.urls import path

from .views.category import CategoryListCreate
from .views.project import (
    ProjectListCreate,
    ProjectRestrictedUpdate,
    ProjectRetrieveUpdate,
)
from .views.project_category import ProjectCategoriesDestroy
from .views.project_commission_date import (
    ProjectCommissionDateListCreate,
    ProjectCommissionDateRetrieve,
    ProjectCommissionDateUpdateDestroy,
)

urlpatterns = [
    # Project categories urls
    path(
        "categories",
        CategoryListCreate.as_view(),
        name="project_categories_list_create",
    ),
    # Project category links urls
    path(
        "<int:project_id>/categories/<int:category_id>",
        ProjectCategoriesDestroy.as_view(),
        name="project_categories_destroy",
    ),
    # Project urls
    path("", ProjectListCreate.as_view(), name="project_list_create"),
    path("<int:pk>", ProjectRetrieveUpdate.as_view(), name="project_retrieve_update"),
    path(
        "<int:pk>/restricted",
        ProjectRestrictedUpdate.as_view(),
        name="project_restricted_update",
    ),
    path(
        "commission_dates",
        ProjectCommissionDateListCreate.as_view(),
        name="project_commission_date_list_create",
    ),
    path(
        "<int:project_id>/commission_dates",
        ProjectCommissionDateRetrieve.as_view(),
        name="project_commission_date_retrieve",
    ),
    path(
        "<int:project_id>/commission_dates/<int:commission_date_id>",
        ProjectCommissionDateUpdateDestroy.as_view(),
        name="project_commission_date_update_destroy",
    ),
]
