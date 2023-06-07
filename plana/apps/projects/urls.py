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
from .views.project_comment import (
    ProjectCommentCreate,
    ProjectCommentRetrieve,
    ProjectCommentUpdateDestroy,
)
from .views.project_commission_fund import (
    ProjectCommissionFundListCreate,
    ProjectCommissionFundRetrieve,
    ProjectCommissionFundUpdateDestroy,
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
        "commission_funds",
        ProjectCommissionFundListCreate.as_view(),
        name="project_commission_fund_list_create",
    ),
    path(
        "<int:project_id>/commission_funds",
        ProjectCommissionFundRetrieve.as_view(),
        name="project_commission_fund_retrieve",
    ),
    path(
        "<int:project_id>/commission_funds/<int:commission_fund_id>",
        ProjectCommissionFundUpdateDestroy.as_view(),
        name="project_commission_fund_update_destroy",
    ),
    path(
        "comments",
        ProjectCommentCreate.as_view(),
        name="project_comment_create",
    ),
    path(
        "<int:project_id>/comments",
        ProjectCommentRetrieve.as_view(),
        name="project_comment_list_create",
    ),
    path(
        "<int:project_id>/comments/<int:comment_id>",
        ProjectCommentUpdateDestroy.as_view(),
        name="project_comment_update_destroy",
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
