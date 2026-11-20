"""Main TestCase for projects managers."""
from django.test import TestCase
from django.utils import timezone

from plana.apps.projects.models import Project


class ProjectQuerySetTestCase(TestCase):
    """Main ProjectQuerySet TestCase"""

    fixtures = [
        "tests/associations_association.json",
        "associations_activityfield.json",
        "auth_group.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/contents_setting.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "projects_category.json",
        "tests/projects_project.json",
        "tests/projects_projectcategory.json",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
    ]

    def test_annotate_bearer_counts(self):
        Project.objects.filter(pk=5).update(planned_end_date=timezone.datetime(year=1990, month=1, day=1))

        project_with_bearer_overdue_review_count = Project.objects.filter(pk=3).annotate_bearer_counts().first()
        self.assertEqual(project_with_bearer_overdue_review_count.bearer_overdue_review_count, 1)

        project_without_bearer_overdue_review_count = Project.objects.filter(pk=4).annotate_bearer_counts().first()
        self.assertEqual(project_without_bearer_overdue_review_count.bearer_overdue_review_count, 0)

    def test_order_by_project_statuses_manage(self):
        """
        Ensure correct order based on fixtures projects
        1 and 2 should be last because their status is not selected in priority queryset (PROJECT_DRAFT)
        """
        ordered_ids = list(Project.objects.all().order_by_project_statuses_manage().values_list("id", flat=True))
        expected_ids = [3, 4, 10, 7, 8, 5, 6, 9, 1, 2]
        self.assertEqual(ordered_ids, expected_ids)
