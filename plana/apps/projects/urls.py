"""List of URLs directly linked to operations that can be done on projects."""
from django.urls import path

from .views.category import CategoryList
from .views.project import (
    ProjectListCreate,
    ProjectRetrieveUpdate,
    ProjectReviewRetrieveUpdate,
    ProjectStatusUpdate,
)
from .views.project_category import (
    ProjectCategoryDestroy,
    ProjectCategoryListCreate,
    ProjectCategoryRetrieve,
)
from .views.project_commission_date import (
    ProjectCommissionDateListCreate,
    ProjectCommissionDateRetrieve,
    ProjectCommissionDateUpdateDestroy,
)
from .views.project_export import ProjectDataExport, ProjectReviewDataExport

urlpatterns = [
    path("", ProjectListCreate.as_view(), name="project_list_create"),
    path("<int:pk>", ProjectRetrieveUpdate.as_view(), name="project_retrieve_update"),
    path(
        "<int:pk>/status",
        ProjectStatusUpdate.as_view(),
        name="project_status_update",
    ),
    path(
        "categories/names",
        CategoryList.as_view(),
        name="category_list",
    ),
    path(
        "categories",
        ProjectCategoryListCreate.as_view(),
        name="project_category_list_create",
    ),
    path(
        "<int:project_id>/categories",
        ProjectCategoryRetrieve.as_view(),
        name="project_category_retrieve",
    ),
    path(
        "<int:project_id>/categories/<int:category_id>",
        ProjectCategoryDestroy.as_view(),
        name="project_category_destroy",
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
    path(
        "<int:pk>/review",
        ProjectReviewRetrieveUpdate.as_view(),
        name="project_review_retrieve_update",
    ),
    path(
        "<int:id>/export",
        ProjectDataExport.as_view(),
        name="project_data_export",
    ),
    path(
        "<int:id>/review/export",
        ProjectReviewDataExport.as_view(),
        name="project_review_data_export",
    ),
]
