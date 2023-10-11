"""List of tests done on associations views."""
import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.history.models.history import History
from plana.apps.users.models.user import AssociationUser

# from django.conf import settings
# from django.core.files.storage import default_storage
# from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
# from unittest.mock import Mock
# from plana.storages import DynamicThumbnailImageField


class AssociationsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_fund.json",
        "documents_document.json",
        "documents_documentupload.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "projects_project.json",
        "users_associationuser.json",
        "users_user.json",
        "users_groupinstitutionfunduser.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on all tests."""
        cls.client = Client()
        url_login = reverse("rest_login")

        # Start a student member of an association client used in some tests
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.member_client = Client()
        data_member = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.member_client.post(url_login, data_member)

        # Start a student president of an association client used in some tests
        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"
        cls.president_client = Client()
        data_president = {
            "username": cls.president_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.president_client.post(url_login, data_president)

        # Start a manager misc client used in some tests
        cls.manager_misc_user_id = 5
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.misc_client = Client()
        data_misc = {
            "username": cls.manager_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.misc_client.post(url_login, data_misc)

        # Start a manager institution client used in some tests
        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

        # Start a manager general client used in some tests
        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.general_client = Client()
        data_general = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.general_client.post(url_login, data_general)

    def test_get_associations_list(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - We get the same amount of associations through the model and through the view.
        - Only associations site and public are returned by default.
        - Main associations details are returned (test the "name" attribute).
        - All associations details aren't returned (test the "current_projects" attribute).
        """
        response = self.client.get("/associations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        associations = Association.objects.filter(is_site=True, is_public=True)
        self.assertEqual(len(response.data), len(associations))

        content = json.loads(response.content.decode("utf-8"))
        association_1 = content[0]
        self.assertTrue(association_1.get("name"))
        self.assertFalse(association_1.get("current_projects"))

    def test_get_associations_list_filter_name(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - An association can be found with its name.
        """
        similar_names = [
            "Plateforme de Liaison et ANnuaire Associatif",
            "plateforme de liaison et annuaire associatif",
            "PlateformedeLiaisonetANnuaireAssociatif",
            "plateformedeliaisonetannuaireassociatif",
            " Plateforme de Liaison et ANnuaire Associatif ",
            "Plàtéfôrmè dê Lîâïsön ët ANnùäire Associatif",
            "plateforme",
        ]
        for similar_name in similar_names:
            response = self.client.get(f"/associations/?name={similar_name}")
            self.assertEqual(response.data[0]["name"], similar_names[0])

    def test_get_associations_list_filter_acronym(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - An association can be found with its acronym.
        """
        similar_acronyms = [
            "PLANA",
            "PlanA",
            " PLANA ",
            "plan",
        ]
        for similar_acronym in similar_acronyms:
            response = self.client.get(f"/associations/?acronym={similar_acronym}")
            self.assertEqual(response.data[0]["acronym"], similar_acronyms[0])

    def test_get_associations_list_filter_enabled(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Enabled associations can be filtered.
        """
        response = self.client.get("/associations/?is_enabled=true")
        for association in response.data:
            self.assertEqual(association["is_enabled"], True)

    def test_get_associations_list_filter_public(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Public associations can be filtered.
        """
        response = self.client.get("/associations/?is_public=true")
        for association in response.data:
            self.assertEqual(association["is_public"], True)

    def test_get_associations_list_filter_site(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Site associations can be filtered.
        """
        response = self.client.get("/associations/?is_site=true")
        for association in response.data:
            self.assertEqual(association["is_site"], True)

    def test_get_associations_list_filter_institution(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Associations with a specific institution ID can be filtered.
        """
        response = self.client.get("/associations/?institutions=1")
        for association in response.data:
            self.assertEqual(association["institution"]["id"], 1)

    def test_get_associations_list_filter_institution_component(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Associations with a specific institution component ID can be filtered.
        - Associations without a specific institution component ID can be filtered.
        """
        response = self.client.get("/associations/?institution_component=1")
        for association in response.data:
            self.assertEqual(association["institution_component"], 1)

        response = self.client.get("/associations/?institution_component=")
        for association in response.data:
            self.assertEqual(association["institution_component"], None)

    def test_get_associations_list_filter_activity_field(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Associations with a specific activity field can be filtered.
        """
        response = self.client.get("/associations/?activity_field=3")
        for association in response.data:
            self.assertEqual(association["activity_field"], 3)

    def test_get_associations_list_filter_user_anonymous(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Associations with a specific user_id cannot be filtered by an anonymous.
        """
        response = self.client.get(f"/associations/?user_id={self.student_user_id}")
        content = json.loads(response.content.decode("utf-8"))
        links_cnt = AssociationUser.objects.filter(user_id=self.student_user_id).count()
        self.assertNotEqual(len(content), links_cnt)

    def test_get_associations_list_filter_user_manager(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Associations with a specific user_id can be filtered by a manager.
        """
        response = self.general_client.get(f"/associations/?user_id={self.student_user_id}")
        content = json.loads(response.content.decode("utf-8"))
        links_cnt = AssociationUser.objects.filter(user_id=self.student_user_id).count()
        self.assertEqual(len(content), links_cnt)

    def test_get_associations_list_filter_non_enabled_student(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Non-enabled associations cannot be filtered by student.
        """
        response = self.member_client.get("/associations/?is_enabled=false")
        for association in response.data:
            self.assertEqual(association["is_enabled"], True)

    def test_get_associations_list_filter_non_enabled_manager(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Non-enabled associations can be filtered by a manager.
        """
        response = self.general_client.get("/associations/?is_enabled=false")
        for association in response.data:
            self.assertEqual(association["is_enabled"], False)

    def test_get_associations_list_filter_non_public_student(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Non-public associations cannot be filtered by student.
        """
        response = self.member_client.get("/associations/?is_public=false")
        for association in response.data:
            self.assertEqual(association["is_public"], True)

    def test_get_associations_list_filter_non_public_manager(self):
        """
        GET /associations/ .

        - The route can be accessed by anyone.
        - Non-public associations can be filtered by a manager.
        """
        response = self.general_client.get("/associations/?is_enabled=false")
        for association in response.data:
            self.assertEqual(association["is_enabled"], False)

        response = self.general_client.get("/associations/?is_public=false")
        for association in response.data:
            self.assertEqual(association["is_public"], False)

    def test_get_association_details_404(self):
        """
        GET /associations/{id} .

        - A non-existing association can't be returned.
        """
        not_found_response = self.client.get("/associations/9999")
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_association_details_forbidden(self):
        """
        GET /associations/{id} .

        - A non-public association can't be seen by an anonymous user.
        - A non-enabled association can't be seen by a student user who's not in it.
        - A non-public association can't be seen by a student user who's not in it.
        """
        non_public_response = self.client.get("/associations/3")
        self.assertEqual(non_public_response.status_code, status.HTTP_403_FORBIDDEN)

        non_enabled_not_member_response = self.member_client.get("/associations/5")
        self.assertEqual(non_enabled_not_member_response.status_code, status.HTTP_403_FORBIDDEN)

        non_public_not_member_response = self.member_client.get("/associations/3")
        self.assertEqual(non_public_not_member_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_association_details_success(self):
        """
        GET /associations/{id} .

        - The route can be accessed by anyone.
        - Main association details are returned (test the "name" attribute).
        - All associations details are returned (test the "current_projects" attribute).
        - A non-enabled association can be seen by a student user who's in it.
        - A non-public association can be seen by a student user who's in it.
        """
        association = Association.objects.get(id=1)

        response = self.client.get("/associations/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        public_association = json.loads(response.content.decode("utf-8"))
        self.assertEqual(public_association["name"], association.name)
        self.assertEqual(public_association["currentProjects"], association.current_projects)

    def test_get_association_details_success_not_enabled(self):
        """
        GET /associations/{id} .

        - A non-enabled association can be seen by a student user who's in it.
        """
        non_enabled_member_response = self.member_client.get("/associations/2")
        self.assertEqual(non_enabled_member_response.status_code, status.HTTP_200_OK)

    def test_get_association_details_success_not_public(self):
        """
        GET /associations/{id} .

        - A non-public association can be seen by a student user who's in it.
        """
        non_public_member_response = self.member_client.get("/associations/2")
        self.assertEqual(non_public_member_response.status_code, status.HTTP_200_OK)

    def test_post_association_bad_request(self):
        """
        POST /associations/ .

        - Name param is mandatory.
        - Institution param is mandatory.
        - Email param is mandatory.
        """
        response_general = self.general_client.post(
            "/associations/",
            {
                "name": "Les Fans de Georges la Saucisse",
            },
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

        response_general = self.general_client.post(
            "/associations/",
            {"institution": 2},
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

        response_general = self.general_client.post(
            "/associations/",
            {
                "name": "Les Fans de Georges la Saucisse",
                "institution": 2,
            },
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_association_404(self):
        """
        POST /associations/ .

        - Institution must exist.
        """
        response_general = self.general_client.post(
            "/associations/",
            {"institution": 1000},
        )
        self.assertEqual(response_general.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_association_anonymous(self):
        """
        POST /associations/ .

        - The user must be authenticated.
        """
        response = self.client.post(
            "/associations/",
            {
                "name": "Quelle chanteuse se connecte sans compte à l'application ? Patricia CAS",
                "institution": 2,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_association_forbidden(self):
        """
        POST /associations/ .

        - An Institution Manager cannot add an association not from the same institution.
        - A Misc manager cannot add an association linked to another institution than its own.
        - A Misc manager cannot set is_site on a new association.
        """
        response_institution = self.institution_client.post(
            "/associations/",
            {
                "name": "Le réalisateur de Star Wars c'est George LuCAS.",
                "institution": 2,
            },
        )
        self.assertEqual(response_institution.status_code, status.HTTP_403_FORBIDDEN)

        response_misc = self.misc_client.post(
            "/associations/",
            {
                "name": "Quand Brice de Nice se connecte via CAS, c'est CASsé.",
                "institution": 2,
            },
        )
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)

        response_misc = self.misc_client.post(
            "/associations/",
            {"name": "Dans mes gâteaux je mets de la CASsonnade.", "is_public": True},
        )
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_association_similar_names(self):
        """
        POST /associations/ .

        - A General Manager can add an association.
        - An association with the same name cannot be added twice.
        - An association cannot have a similar name compared to another one.
        """
        response_general = self.general_client.post(
            "/associations/",
            {
                "name": "Les Fans de Georges la Saucisse",
                "institution": 2,
                "email": "mail@mail.tld",
            },
        )

        similar_names = [
            "Les Fans de Georges la Saucisse",
            "LesFansdeGeorgeslaSaucisse",
            "lesfansdegeorgeslasaucisse",
            " Les Fans de Georges la Saucisse ",
            "Lés Fàns dè Gêörgës lâ Säùcîsse",
        ]
        for similar_name in similar_names:
            response_general = self.general_client.post(
                "/associations/",
                {"name": similar_name, "institution": 2},
            )
            self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_association_serializer_error(self):
        """
        POST /associations/ .

        - A General Manager can add an association.
        - Serializers fields must be valid.
        """
        response_general = self.general_client.post(
            "/associations/",
            data={"name": "Nom d'asso", "institution": 2, "email": False},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_association_success_manager_institution(self):
        """
        POST /associations/ .

        - An Institution Manager can add an association from the same institution.
        """
        response_institution = self.institution_client.post(
            "/associations/",
            {
                "name": "Le plat phare du sud-ouest de la France c'est le CASsoulet.",
                "email": "cassoulet@toulouse.fr",
            },
        )
        self.assertEqual(response_institution.status_code, status.HTTP_201_CREATED)
        no_site_association = json.loads(response_institution.content.decode("utf-8"))
        self.assertFalse(no_site_association["isPublic"])
        new_association = json.loads(response_institution.content.decode("utf-8"))
        self.assertEqual(new_association["institution"], 3)

    def test_post_association_success_manager_general(self):
        """
        POST /associations/ .

        - A General Manager can add an association.
        - A General Manager can add a site association.
        """
        response_general = self.general_client.post(
            "/associations/",
            {
                "name": "Les Fans de Georges la Saucisse",
                "email": "fan-2-georges@mail.tld",
                "institution": 2,
            },
        )
        self.assertEqual(response_general.status_code, status.HTTP_201_CREATED)
        non_site_association = json.loads(response_general.content.decode("utf-8"))
        self.assertFalse(non_site_association["isSite"])

        response_general = self.general_client.post(
            "/associations/",
            {
                "name": "Les gens qui savent imiter Bourvil",
                "email": "ah-bah-mon-velo@mail.tld",
                "institution": 2,
                "is_public": True,
            },
        )
        self.assertEqual(response_general.status_code, status.HTTP_201_CREATED)
        site_association = json.loads(response_general.content.decode("utf-8"))
        self.assertTrue(site_association["isPublic"])

    def test_put_association(self):
        """
        PUT /associations/{id} .

        - Always returns a 405 no matter which user tries to access it.
        """
        response = self.client.put("/associations/1", {"name": "Les aficionados d'endives au jambon"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_association_anonymous(self):
        """
        PATCH /associations/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.patch(
            "/associations/1",
            {"name": "La Grande Confrérie du Cassoulet de Castelnaudary"},
            content_type="application/json",
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_association_wrong_phone_number(self):
        """
        PATCH /associations/{id} .

        - A member of the association's office can edit information from the association.
        - Phone number must respect a given format.
        """
        association_id = 2
        response_president = self.president_client.patch(
            f"/associations/{association_id}",
            {"phone": "Waluigi"},
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)
        association = Association.objects.get(id=association_id)
        self.assertNotEqual(association.phone, "Waluigi")

    def test_patch_association_manager_misc(self):
        """
        PATCH /associations/{id} .

        - A Misc Manager cannot edit an association.
        """
        response_misc = self.misc_client.patch(
            "/associations/1",
            {"name": "L'assaucissiation"},
            content_type="application/json",
        )
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_association_404(self):
        """
        PATCH /associations/{id} .

        - A non-existing association cannot be edited.
        """
        association_id = 99
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"name": "La singularité de l'espace-temps."},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_association_not_members(self):
        """
        PATCH /associations/{id} .

        - A member of an association without status cannot edit infos from another association.
        - A member of an association's office cannot edit information from another association.
        """
        association_id = 3
        response_incorrect_member = self.member_client.patch(
            f"/associations/{association_id}",
            {"name": "Je suis pas de cette asso mais je veux l'éditer."},
            content_type="application/json",
        )
        self.assertEqual(response_incorrect_member.status_code, status.HTTP_403_FORBIDDEN)
        response_incorrect_president = self.president_client.patch(
            f"/associations/{association_id}",
            {"name": "Je suis membre du bureau d'une autre asso, mais je veux l'éditer."},
            content_type="application/json",
        )
        self.assertEqual(response_incorrect_president.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_association_by_its_members_forbidden(self):
        """
        PATCH /associations/{id} .

        - A member of the association without status cannot edit infos from the association.
        """
        association_id = 2
        response_correct_member = self.member_client.patch(
            f"/associations/{association_id}",
            {"name": "Ah et bah moi je suis de l'asso mais je peux pas l'éditer c'est terrible."},
            content_type="application/json",
        )
        self.assertEqual(response_correct_member.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(len(mail.outbox))

    def test_patch_association_by_its_members_success(self):
        """
        PATCH /associations/{id} .

        - A member of the association's office can edit information from the association.
        - Event is stored in History.
        - An email is received if change is successful.
        """
        association_id = 2
        response_correct_president = self.president_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Moi je peux vraiment éditer l'asso, nananère.",
                "phone": "0836656565",
            },
            content_type="application/json",
        )
        self.assertEqual(response_correct_president.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_CHANGED").count(), 1)
        association = Association.objects.get(id=association_id)
        self.assertEqual(
            association.name,
            "Moi je peux vraiment éditer l'asso, nananère.",
        )
        self.assertTrue(len(mail.outbox))

    def test_patch_association_manager_success(self):
        """
        PATCH /associations/{id} .

        - A General Manager can edit an association.
        - Event is stored in History.
        - An email is received if change is successful.
        - can_submit_projects can be set by a manager.
        """
        association_id = 1

        self.assertFalse(len(mail.outbox))
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Association Amicale des Amateurs d'Andouillette Authentique",
                "institution": 1,
                "can_submit_projects": False,
            },
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_CHANGED").count(), 1)
        association = Association.objects.get(id=association_id)
        self.assertEqual(
            association.name,
            "Association Amicale des Amateurs d'Andouillette Authentique",
        )
        self.assertEqual(association.institution_id, 1)
        self.assertEqual(association.can_submit_projects, False)
        self.assertTrue(len(mail.outbox))

        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"can_submit_projects": True},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.can_submit_projects, True)

    def test_patch_association_lower_amount_members(self):
        """
        PATCH /associations/{id} .

        - Cannot lower max number of student allowed in an association if all of them are registered.
        """
        association_id = 2
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"amount_members_allowed": 1},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_association_social_networks_bad_request(self):
        """
        PATCH /associations/{id} .

        - Association's social networks are not updated if the keys are not valid (400).
        - Association's social networks are not updated if the values are not strings (400).
        """
        association_id = 2
        response_general_keys = self.general_client.patch(
            f"/associations/{association_id}",
            {
                "social_networks": json.dumps(
                    [
                        {
                            "typeeee": "Mastodon",
                            "location": "https://framapiaf.org/@Framasoft",
                        }
                    ]
                )
            },
            content_type="application/json",
        )
        self.assertEqual(response_general_keys.status_code, status.HTTP_400_BAD_REQUEST)

        response_general_string = self.general_client.patch(
            f"/associations/{association_id}",
            {"social_networks": json.dumps([{"type": "Mastodon", "location": 1234}])},
            content_type="application/json",
        )
        self.assertEqual(response_general_string.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_association_social_networks_success(self):
        """
        PATCH /associations/{id} .

        - A General Manager can edit an association's social networks.
        - Event is stored in History.
        - Association's social networks are correctly updated with provided data.
        """
        association_id = 2
        social_networks_json = json.dumps([{"type": "Mastodon", "location": "https://framapiaf.org/@Framasoft"}])
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"social_networks": social_networks_json},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_CHANGED").count(), 1)
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.social_networks, social_networks_json)

    def test_patch_association_public_or_not(self):
        """
        PATCH /associations/{id} .

        - An association can't be public if not enabled.
        - An association must be lost public status if enabled or site is removed.
        """
        # This association is not enabled by default
        association_id = 3
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": False},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_enabled, False)

        # Association public status can be true only if is_enabled is true
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": True},
            content_type="application/json",
        )
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_public": True},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, True)

        # Association loosing its public status by changing is_enabled to false
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": False},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

    def test_patch_association_logo(self):
        """
        PATCH /associations/{id} .

        - Association's logo can be updated.
        - Returns 415 if MIME type is wrong.
        """
        # TODO Find how to mock images.
        """
        association_id = 1
        data = encode_multipart(data={"path_logo": file}, boundary=BOUNDARY)
        response = self.general_client.patch(
            f"/associations/{association_id}", data=data, content_type=MULTIPART_CONTENT
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        settings.ALLOWED_IMAGE_MIME_TYPES = ["application/vnd.novadigm.ext"]
        response = self.general_client.patch(
            f"/associations/{association_id}", data, content_type=MULTIPART_CONTENT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        """

    def test_delete_association_anonymous(self):
        """
        DELETE /associations/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete("/associations/1")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_association_forbidden(self):
        """
        DELETE /associations/{id} .

        - An enabled association cannot be deleted.
        - A Misc Manager cannot delete an association.
        - An Institution Manager cannot delete an association from another institution.
        """
        association_id = 1

        response_general = self.general_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_general.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(len(mail.outbox))

        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": False},
            content_type="application/json",
        )

        response_misc = self.misc_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)

        response_institution = self.institution_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_institution.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_association_404(self):
        """
        DELETE /associations/{id} .

        - A non-existing association cannot be deleted.
        """
        response_general = self.general_client.delete("/associations/9999")
        self.assertEqual(response_general.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_association_success(self):
        """
        DELETE /associations/{id} .

        - A General Manager can delete an association.
        - An email is received if deletion is successful.
        - Association object is correctly deleted from db.
        """
        association_id = 5
        association = Association.objects.get(id=association_id)
        association.is_enabled = False
        association.save()

        response_general = self.general_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_general.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(len(mail.outbox))
        with self.assertRaises(ObjectDoesNotExist):
            Association.objects.get(id=association_id)

    def test_put_association_status(self):
        """
        PUT /associations/{id}/status .

        - Always returns a 405.
        """
        patch_data = {"charter_status": "CHARTER_REJECTED"}
        response = self.general_client.put("/associations/2/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_association_status_anonymous(self):
        """
        PATCH /associations/{id}/status .

        - An anonymous user cannot execute this request.
        """
        patch_data = {"charter_status": "CHARTER_REJECTED"}
        response = self.client.patch("/associations/2/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_association_status_not_found(self):
        """
        PATCH /associations/{id}/status .

        - Association must exist.
        """
        patch_data = {"charter_status": "CHARTER_REJECTED"}
        response = self.general_client.patch("/associations/999/status", patch_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_association_status_wrong_student(self):
        """
        PATCH /associations/{id}/status .

        - An student user cannot execute this request if not president.
        """
        association_id = 2
        patch_data = {"charter_status": "CHARTER_PROCESSING"}
        response = self.member_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_association_status_serializer_error(self):
        """
        PATCH /associations/{id}/status .

        - A manager user can execute this request.
        - Serializer fields must be valid.
        """
        association_id = 2
        patch_data = {"charter_status": False}
        response = self.general_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_association_status_student(self):
        """
        PATCH /associations/{id}/status .

        - An student user cannot execute this request if status is not allowed.
        - An student user can execute this request if status is allowed.
        - Event is stored in History.
        """
        association_id = 2
        self.assertFalse(len(mail.outbox))
        patch_data = {"charter_status": "CHARTER_REJECTED"}
        response = self.president_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(len(mail.outbox))

        patch_data = {"charter_status": "CHARTER_PROCESSING"}
        response = self.president_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_CHARTER_CHANGED").count(), 1)
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.charter_status, "CHARTER_PROCESSING")
        self.assertTrue(len(mail.outbox))

    def test_patch_association_status_manager(self):
        """
        PATCH /associations/{id}/status .

        - A manager user can execute this request.
        """
        association_id = 2
        self.assertFalse(len(mail.outbox))
        patch_data = {"charter_status": "CHARTER_REJECTED"}
        response = self.general_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.charter_status, "CHARTER_REJECTED")
        self.assertEqual(association.is_site, False)
        self.assertTrue(len(mail.outbox))

        patch_data = {"charter_status": "CHARTER_VALIDATED"}
        response = self.general_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.charter_status, "CHARTER_VALIDATED")
        self.assertEqual(association.is_site, True)

    def test_patch_association_status_missing_documents(self):
        """
        PATCH /associations/{id}/status .

        - The route can be accessed by a student president.
        - Association cannot be updated if documents are missing.
        """
        document = Document.objects.get(acronym="COPIE_STATUTS_ASSOCIATION")
        association_id = 2
        DocumentUpload.objects.get(document_id=document.id, association_id=2).delete()
        patch_data = {"charter_status": "CHARTER_PROCESSING"}
        response = self.president_client.patch(
            f"/associations/{association_id}/status",
            patch_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        association = Association.objects.get(id=association_id)
        self.assertNotEqual(association.charter_status, "CHARTER_PROCESSING")

    def test_get_activity_fields_list(self):
        """
        GET /associations/activity_fields .

        - There's at least one activity field in the activity fields list.
        - The route can be accessed by anyone.
        - We get the same amount of activity fields through the model and through the view.
        - Activity fields details are returned (test the "name" attribute).
        """
        activity_fields_cnt = ActivityField.objects.count()
        self.assertTrue(activity_fields_cnt > 0)

        response = self.client.get("/associations/activity_fields")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), activity_fields_cnt)

        activity_field_1 = content[0]
        self.assertTrue(activity_field_1.get("name"))

    def test_get_association_names_list(self):
        """
        GET /associations/names .

        - The route can be accessed by anyone.
        - We get the same amount of associations through the model and through the view.
        - Only id and names of the associations are returned.
        """
        response = self.client.get("/associations/names")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        associations = Association.objects.all()
        self.assertEqual(len(response.data), len(associations))

        content_all_assos = json.loads(response.content.decode("utf-8"))
        asso_name_1 = content_all_assos[0]
        self.assertTrue(asso_name_1.get("name"))
        self.assertTrue(asso_name_1.get("id"))
        self.assertFalse(asso_name_1.get("institution_component"))

    def test_get_association_names_list_filter_institution(self):
        """
        GET /associations/names .

        - The route can be accessed by anyone.
        - Get the same amount of associations by institution through model and view.
        """
        asso_names_cnt_institution = Association.objects.filter(institution_id__in=[2, 3]).count()
        response = self.client.get("/associations/names?institutions=2,3")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), asso_names_cnt_institution)

    def test_get_association_names_list_filter_public(self):
        """
        GET /associations/names .

        - The route can be accessed by anyone.
        - Get the same amount of public associations through model and view.
        """
        asso_names_cnt_public = Association.objects.filter(is_public=True).count()
        response = self.client.get("/associations/names?is_public=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), asso_names_cnt_public)

    def test_get_association_names_list_allow_new_user(self):
        """
        GET /associations/names .

        - The route can be accessed by anyone.
        - Get a different amount of associations with allow_new_users filter.
        """
        response = self.client.get("/associations/names")
        content_all_assos = json.loads(response.content.decode("utf-8"))

        AssociationUser.objects.create(user_id=12, association_id=2)

        response_assos_users_allowed = self.client.get("/associations/names?allow_new_users=true")
        content_assos_users_allowed = json.loads(response_assos_users_allowed.content.decode("utf-8"))
        response_assos_users_not_allowed = self.client.get("/associations/names?allow_new_users=false")
        content_assos_users_not_allowed = json.loads(response_assos_users_not_allowed.content.decode("utf-8"))
        self.assertEqual(
            len(content_assos_users_allowed) + len(content_assos_users_not_allowed),
            len(content_all_assos),
        )
