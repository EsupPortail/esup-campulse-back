"""List of tests done on projects views."""

import datetime
import json

from django.core import mail
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.history.models.history import History
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser


class ProjectsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_fund.json",
        "commissions_commission.json",
        "commissions_commissionfund.json",
        "contents_setting.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_category.json",
        "projects_project.json",
        "projects_projectcategory.json",
        "projects_projectcommissionfund.json",
        "users_associationuser.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start clients used on tests."""
        cls.client = Client()
        url_login = reverse("rest_login")

        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.general_client = Client()
        data_general = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.general_client.post(url_login, data_general)

        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

        cls.fund_user_id = 6
        cls.fund_user_name = "membre-fsdie-idex@mail.tld"
        cls.fund_client = Client()
        data_fund = {
            "username": cls.fund_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.fund_client.post(url_login, data_fund)

        cls.student_misc_user_id = 9
        cls.student_misc_user_name = "etudiant-porteur@mail.tld"
        cls.student_misc_client = Client()
        data_student_misc = {
            "username": cls.student_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_misc_client.post(url_login, data_student_misc)

        cls.student_offsite_user_id = 10
        cls.student_offsite_user_name = "etudiant-asso-hors-site@mail.tld"
        cls.student_offsite_client = Client()
        data_student_offsite = {
            "username": cls.student_offsite_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_offsite_client.post(url_login, data_student_offsite)

        cls.student_site_user_id = 11
        cls.student_site_user_name = "etudiant-asso-site@mail.tld"
        cls.student_site_client = Client()
        data_student_site = {
            "username": cls.student_site_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_site_client.post(url_login, data_student_site)

        cls.student_president_user_id = 13
        cls.student_president_user_name = "president-asso-site@mail.tld"
        cls.student_president_client = Client()
        data_student_president = {
            "username": cls.student_president_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.student_president_client.post(url_login, data_student_president)

    def test_get_project_anonymous(self):
        """
        GET /projects/ .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_student(self):
        """
        GET /projects/ .

        - A student user gets projects where rights are OK.
        """
        ProjectCommissionFund.objects.get(project_id=1).delete()
        response = self.student_misc_client.get("/projects/")
        user_associations_ids = AssociationUser.objects.filter(user_id=self.student_misc_user_id).values_list(
            "association_id"
        )
        user_projects_cnt = Project.visible_objects.filter(
            models.Q(user_id=self.student_misc_user_id) | models.Q(association_id__in=user_associations_ids)
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), user_projects_cnt)

    def test_get_project_fund_member(self):
        """
        GET /projects/ .

        - A fund member gets only validated projects.
        """
        response = self.fund_client.get("/projects/")
        fund_projects_cnt = Project.visible_objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    fund_id__in=GroupInstitutionFundUser.objects.filter(user_id=self.fund_user_id).values_list(
                        "fund_id"
                    )
                ).values_list("id")
            ).values_list("project_id"),
            project_status__in=Project.ProjectStatus.get_commissionnable_project_statuses(),
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), fund_projects_cnt)

    def test_get_project_institution(self):
        """
        GET /projects/ .

        - An institution manager gets projects where rights are OK.
        """
        response = self.institution_client.get("/projects/")
        user_institutions_ids = Institution.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(user_id=self.manager_institution_user_id).values_list(
                "institution_id"
            )
        )
        association_projects_cnt = Project.visible_objects.filter(
            association_id__in=Association.objects.filter(institution_id__in=user_institutions_ids).values_list("id")
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), association_projects_cnt)

    def test_get_project_manager(self):
        """
        GET /projects/ .

        - A general manager user gets all projects.
        - Search filters are available.
        """
        response = self.general_client.get("/projects/")
        projects_cnt = Project.visible_objects.all().count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), projects_cnt)

        similar_names = [
            "Projet associatif de porteur de projet individuel",
            "projet associatif de porteur de projet individuel",
            "Projetassociatifdeporteurdeprojetindividuel",
            "projetassociatifdeporteurdeprojetindividuel",
            " Projet associatif de porteur de projet individuel ",
            "Prôjêt àssöcïâtîf dë porteur de projet individuel",
            "associatif de porteur de projet individuel",
        ]
        for similar_name in similar_names:
            response = self.general_client.get(f"/projects/?name={similar_name}")
            self.assertEqual(response.data[0]["name"], similar_names[0])

        similar_identifiers = [
            "20890001",
            "2089 0001",
            "2089",
        ]
        for similar_identifier in similar_identifiers:
            response = self.general_client.get(f"/projects/?manual_identifier={similar_identifier}")
            self.assertEqual(response.data[0]["manual_identifier"], similar_identifiers[0])

        year = 2099
        response = self.general_client.get(f"/projects/?year={year}")
        projects_cnt = Project.visible_objects.filter(creation_date__year=year).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), projects_cnt)

        response = self.general_client.get(f"/projects/?user_id={self.student_misc_user_id}")
        projects_cnt = Project.visible_objects.filter(user_id=self.student_misc_user_id).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), projects_cnt)

        association_id = 2
        response = self.general_client.get(f"/projects/?association_id={association_id}")
        projects_cnt = Project.visible_objects.filter(association_id=association_id).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), projects_cnt)

        project_statuses = ["PROJECT_DRAFT", "PROJECT_VALIDATED"]
        response = self.general_client.get(f"/projects/?project_statuses={','.join(str(x) for x in project_statuses)}")
        projects_cnt = Project.visible_objects.filter(project_status__in=project_statuses).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), projects_cnt)

        commission = 2
        response = self.general_client.get(f"/projects/?commission_id={commission}")
        projects_cnt = Project.visible_objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(commission_id=commission).values_list("id")
            ).values_list("project_id")
        ).count()
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), projects_cnt)

        projects_ids_with_comments = ProjectComment.objects.all().values_list("project_id")
        response = self.general_client.get("/projects/?with_comments=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), len(projects_ids_with_comments))
        response = self.general_client.get("/projects/?with_comments=false")
        content = json.loads(response.content.decode("utf-8"))
        self.assertNotEqual(len(content), len(projects_ids_with_comments))

        inactive_statuses = Project.ProjectStatus.get_archived_project_statuses()
        inactive_projects = Project.visible_objects.filter(project_status__in=inactive_statuses)
        response = self.general_client.get("/projects/?active_projects=false")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), inactive_projects.count())
        active_projects = Project.visible_objects.exclude(project_status__in=inactive_statuses)
        response = self.general_client.get("/projects/?active_projects=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), active_projects.count())

    def test_post_project_anonymous(self):
        """
        POST /projects/ .

        - An anonymous user cannot execute this request.
        """
        response = self.client.post("/projects/", {"name": "Testing anonymous"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_project_bad_request(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - Project must have at least one affectation (user or association).
        - If linked to an association, the association must already exist.
        - Project cannot have multiple affectations.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "planned_location": "address",
        }
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project_data["association"] = 9999
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        project_data["association"] = 2
        project_data["user"] = self.student_president_user_id
        GroupInstitutionFundUser.objects.create(user_id=self.student_president_user_id, group_id=6)
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_forbidden_user(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - User must have 'can_submit_projects' attribute set to True to sumbit a project.
        - User in the request must be the authenticated user.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "planned_location": "address",
            "user": 10,
        }
        response = self.student_offsite_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        project_data["user"] = 999
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_forbidden_association(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - Association must have 'can_submit_associations' attribute set to True to submit projects.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "planned_location": "address",
            "association": 3,
        }
        response = self.student_offsite_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_forbidden_association_role(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - The authenticated user must be a member of the association to create projects related to it.
        - User must be president or delegated president of its association to submit projects.
        """
        project_data = {
            "name": "Testing creation",
            "goals": "Goals",
            "planned_location": "address",
            "association": 1,
        }
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        project_data["association"] = 2
        response = self.student_site_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_project_association_wrong_audience(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - Number of students in audience cannot exceed number of all people in audience.
        """
        project_data = {
            "name": "Testing creation",
            "association": 2,
            "association_user": 5,
            "amount_students_audience": 1000,
            "amount_all_audience": 8,
        }
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_association_wrong_dates(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - Planned start date cannot be set after planned end date.
        """
        project_data = {
            "name": "Testing creation",
            "association": 2,
            "association_user": 5,
            "planned_start_date": "2099-12-25T14:00:00.000Z",
            "planned_end_date": "2099-11-30T18:00:00.000Z",
        }
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_wrong_association_user(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - A linked user from an association cannot be added to a user project.
        """
        project_data = {
            "name": "Testing creation association",
            "goals": "Goals",
            "planned_location": "address",
            "user": 9,
            "association_user": 2,
        }
        response = self.student_misc_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_association_wrong_user(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - The linked user from the association must be set with an association.
        - The linked user from the association must be correct.
        """
        project_data = {
            "name": "Testing creation association",
            "goals": "Goals",
            "planned_location": "address",
            "association_user": 2,
        }
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project_data["association"] = 2
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_project_serializer_error(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - To create a project for an association, the authenticated user must be president.
        - Serializer fields must be valid.
        """
        project_data = {
            "name": "Testing bad serializer",
            "goals": False,
            "association": 2,
            "association_user": 5,
        }
        response = self.student_president_client.post("/projects/", data=project_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_project_association_success(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - To create a project for an association, the authenticated user must be president.
        - Project is created in database.
        """
        project_data = {
            "name": "Testing creation association",
            "goals": "Goals",
            "planned_location": "address",
            "association": 2,
            "association_user": 5,
        }
        response = self.student_president_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = Project.visible_objects.filter(name="Testing creation association")
        self.assertEqual(len(results), 1)

    def test_post_project_user_success(self):
        """
        POST /projects/ .

        - The route can be accessed by a student user.
        - The user in the request must be the authenticated user.
        - Project is created in database.
        """
        project_data = {
            "name": "Testing creation user",
            "goals": "Goals",
            "planned_location": "address",
            "user": self.student_misc_user_id,
        }
        response = self.student_misc_client.post("/projects/", project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        results = Project.visible_objects.filter(name="Testing creation user")
        self.assertEqual(len(results), 1)

    def test_get_project_by_id_anonymous(self):
        """
        GET /projects/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.get("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_by_id_404(self):
        """
        GET /projects/{id} .

        - The route returns a 404 if a wrong project id is given.
        """
        response = self.general_client.get("/projects/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_by_id_forbidden_student(self):
        """
        GET /projects/{id} .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.get("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_by_id_forbidden_fund_member(self):
        """
        GET /projects/{id} .

        - An fund member cannot see a project not linked to the fund.
        - An fund member cannot see an unvalidated project.
        """
        response = self.fund_client.get("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.fund_client.get("/projects/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_project_by_id(self):
        """
        GET /projects/{id} .

        - The route can be accessed by a manager user.
        - The route can be accessed by a student user.
        - Correct projects details are returned (test the "name" attribute).
        """
        project_id = 1
        project_test = Project.visible_objects.get(id=project_id)
        response = self.general_client.get(f"/projects/{project_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["name"], project_test.name)

        project_id = 2
        project_test = Project.visible_objects.get(id=project_id)
        response = self.student_president_client.get(f"/projects/{project_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["name"], project_test.name)

    def test_put_project(self):
        """
        PUT /projects/{id} .

        - Always returns a 405.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.general_client.put("/projects/1", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_anonymous(self):
        """
        PATCH /projects/{id} .

        - An anonymous user cannot execute this request.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.client.patch("/projects/1", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_not_found(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Project must exist.
        """
        patch_data = {"goals": "Testing patching"}
        response = self.student_misc_client.patch("/projects/999", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_forbidden_student(self):
        """
        PATCH /projects/{id} .

        - An student user not owning the project cannot execute this request.
        """
        patch_data = {"name": "Test anonymous"}
        response = self.student_offsite_client.patch("/projects/1", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_forbidden_user(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - The project owner must be the authenticated user.
        """
        patch_data = {"description": "new desc"}
        response = self.student_site_client.patch("/projects/1", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_user_wrong_status(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Status must be draft.
        """
        project_id = 3
        patch_data = {"summary": "new summary"}
        response = self.student_misc_client.patch(
            f"/projects/{project_id}", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_expired_commission(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - The project must be linked to non expired commission dates.
        """
        expired_commission_date = Commission.objects.get(id=1)
        expired_commission_date.submission_date = "1968-05-03"
        expired_commission_date.save()
        patch_data = {"summary": "new summary"}
        response = self.student_misc_client.patch("/projects/1", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_association_wrong_audience(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Number of students in audience cannot exceed number of all people in audience.
        """
        project_data = {
            "amount_students_audience": 1000,
            "amount_all_audience": 8,
        }
        response = self.student_president_client.patch("/projects/2", project_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_association_wrong_dates(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Planned start date cannot be set after planned end date.
        """
        project_data = {
            "planned_start_date": "2099-12-25T14:00:00.000Z",
            "planned_end_date": "2099-11-30T18:00:00.000Z",
        }
        response = self.student_president_client.patch("/projects/2", project_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_wrong_association_user(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - A linked user from an association cannot be added to a user project.
        """
        project_data = {"association_user": 2}
        response = self.student_misc_client.patch("/projects/1", project_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_association_wrong_user(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - The linked user from the association must be correct.
        """
        project_data = {"association_user": 2}
        response = self.student_president_client.patch("/projects/2", project_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_serializer_error(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - Serializer fields must be valid.
        """
        project_id = 1
        patch_data = {"summary": False}
        response = self.student_misc_client.patch(
            f"/projects/{project_id}", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_manager_success(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a manager user, but for some fields only.
        """
        project_id = 1
        patch_data = {
            "description": "new desc",
            "planned_end_date": "2099-12-25T14:00:00.000000Z",
        }
        response = self.general_client.patch(f"/projects/{project_id}", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        project = Project.visible_objects.get(id=project_id)
        self.assertNotEqual(project.description, patch_data["description"])
        self.assertEqual(
            project.planned_end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            patch_data["planned_end_date"],
        )

    def test_patch_project_user_success(self):
        """
        PATCH /projects/{id} .

        - The route can be accessed by a student user.
        - The project is correctly updated in db.
        """
        project_id = 1
        patch_data = {"summary": "new summary"}
        response = self.student_misc_client.patch(
            f"/projects/{project_id}", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=project_id)
        self.assertEqual(project.summary, "new summary")

    def test_delete_project_anonymous(self):
        """
        DELETE /projects/{id} .

        - An anonymous user cannot execute this request.
        """
        response = self.client.delete("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_not_found(self):
        """
        DELETE /projects/{id} .

        - The route can be accessed by a student user.
        - Project must exist.
        """
        response = self.student_misc_client.delete("/projects/999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_forbidden_student(self):
        """
        DELETE /projects/{id} .

        - An student user not owning the project cannot execute this request.
        """
        response = self.student_offsite_client.delete("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_forbidden_user(self):
        """
        DELETE /projects/{id} .

        - The route can be accessed by a student user.
        - The project owner must be the authenticated user.
        """
        response = self.student_site_client.delete("/projects/1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_user_success(self):
        """
        DELETE /projects/{id} .

        - The route can be accessed by a student user.
        - The project is correctly deleted in db.
        """
        project_id = 1
        response = self.student_misc_client.delete(f"/projects/{project_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, len(Project.visible_objects.filter(id=project_id)))

        project_id = 3
        response = self.student_misc_client.delete(f"/projects/{project_id}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(1, len(Project.visible_objects.filter(id=project_id)))

    def test_put_project_status(self):
        """
        PUT /projects/{id}/status .

        - Always returns a 405.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.general_client.put("/projects/5/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_project_status_anonymous(self):
        """
        PATCH /projects/{id}/status .

        - An anonymous user cannot execute this request.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.client.patch("/projects/1/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_project_status_forbidden(self):
        """
        PATCH /projects/{id}/status .

        - A student must have correct permissions to execute this request.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.student_misc_client.patch(
            "/projects/2/status", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_status_not_found(self):
        """
        PATCH /projects/{id}/status .

        - Project must exist.
        """
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.general_client.patch("/projects/999/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_status_serializer_error(self):
        """
        PATCH /projects/{id}/status .

        - A student user can execute this request if status is allowed.
        - Serializer fields must be valid.
        """
        patch_data = {"project_status": False}
        response = self.student_misc_client.patch(
            "/projects/1/status", data=patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_project_status_student(self):
        """
        PATCH /projects/{id}/status .

        - An student user cannot execute this request if status is not allowed.
        - An student user can execute this request if status is allowed.
        """
        self.assertFalse(len(mail.outbox))
        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.student_misc_client.patch("/projects/1/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(len(mail.outbox))

        patch_data = {"project_status": "PROJECT_PROCESSING"}
        response = self.student_misc_client.patch("/projects/1/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=1)
        self.assertEqual(project.project_status, "PROJECT_PROCESSING")
        self.assertTrue(len(mail.outbox))

        response = self.student_president_client.patch(
            "/projects/2/status", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=2)
        self.assertEqual(project.project_status, "PROJECT_PROCESSING")

    def test_patch_project_status_manager(self):
        """
        PATCH /projects/{id}/status .

        - A manager user cannot execute this request if status is not allowed.
        - Statuses must follow order defined in ProjectStatus sub-model.
        - A manager user can execute this request if status is allowed.
        - PROJECT_VALIDATED Event is stored in History.
        - Archived statuses cannot be updated anymore.
        - Cannot rollback to a previous status, except if allowed in order.
        """
        project_id = 3
        patch_data = {"project_status": "PROJECT_REVIEW_PROCESSING"}
        response = self.general_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        patch_data = {"project_status": "PROJECT_REVIEW_DRAFT"}
        response = self.general_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        patch_data = {"project_status": "PROJECT_REJECTED"}
        response = self.general_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=project_id)
        self.assertEqual(project.project_status, "PROJECT_REJECTED")

        patch_data = {"project_status": "PROJECT_VALIDATED"}
        response = self.general_client.patch(
            "/projects/4/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="PROJECT_VALIDATED").count(), 1)
        project = Project.visible_objects.get(id=4)
        self.assertEqual(project.project_status, "PROJECT_VALIDATED")

        patch_data = {"project_status": "PROJECT_REVIEW_DRAFT"}
        response = self.general_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project = Project.visible_objects.get(id=project_id)
        project.project_status = "PROJECT_REVIEW_DRAFT"
        project.save()
        patch_data = {"project_status": "PROJECT_VALIDATED"}
        response = self.general_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        project = Project.visible_objects.get(id=project_id)
        project.project_status = "PROJECT_REVIEW_PROCESSING"
        project.save()
        patch_data = {"project_status": "PROJECT_REVIEW_DRAFT"}
        response = self.general_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_project_association_status_missing_documents(self):
        """
        PATCH /projects/{id}/status .

        - The route can be accessed by a student president.
        - Project cannot be updated if documents are missing.
        """
        document = Document.objects.get(id=19)
        DocumentUpload.objects.get(document=document.id, project_id=2).delete()
        ProjectCommissionFund.objects.create(project_id=2, commission_fund_id=3)
        patch_data = {"project_status": "PROJECT_PROCESSING"}
        response = self.student_president_client.patch(
            "/projects/2/status", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        project = Project.visible_objects.get(id=2)
        self.assertEqual(project.project_status, "PROJECT_DRAFT")

    def test_patch_project_processing_association_status(self):
        """
        PATCH /projects/{id}/status .

        - The route can be accessed by a student president.
        - The project is correctly updated in db.
        """
        self.assertFalse(len(mail.outbox))
        patch_data = {"project_status": "PROJECT_PROCESSING"}
        response = self.student_president_client.patch(
            "/projects/2/status", patch_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=2)
        self.assertEqual(project.project_status, "PROJECT_PROCESSING")
        self.assertTrue(len(mail.outbox))

    def test_patch_project_review_processing_association_status(self):
        """
        PATCH /projects/{id}/status .

        - The route can be accessed by a student president.
        - The project is correctly updated in db.
        """
        project_id = 6
        project = Project.visible_objects.get(id=project_id)
        project.project_status = "PROJECT_REVIEW_DRAFT"
        project.save()

        self.assertFalse(len(mail.outbox))
        ProjectCommissionFund.objects.create(project_id=project_id, commission_fund_id=3)
        patch_data = {"project_status": "PROJECT_REVIEW_PROCESSING"}
        response = self.student_president_client.patch(
            f"/projects/{project_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.visible_objects.get(id=project_id)
        self.assertEqual(project.project_status, "PROJECT_REVIEW_PROCESSING")
        self.assertTrue(len(mail.outbox))
