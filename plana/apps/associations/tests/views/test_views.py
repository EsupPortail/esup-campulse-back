"""List of tests done on associations views."""
import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import AssociationUser


class AssociationsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_commission.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationuser.json",
        "users_user.json",
        "users_groupinstitutioncommissionuser.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on all tests."""
        cls.client = Client()
        url_login = reverse("rest_login")

        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.member_client = Client()
        data_member = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.member_client.post(url_login, data_member)

        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"
        cls.president_client = Client()
        data_president = {
            "username": cls.president_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.president_client.post(url_login, data_president)

        cls.manager_misc_user_id = 5
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.misc_client = Client()
        data_misc = {
            "username": cls.manager_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.misc_client.post(url_login, data_misc)

        cls.manager_institution_user_id = 4
        cls.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        cls.institution_client = Client()
        data_institution = {
            "username": cls.manager_institution_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.institution_client.post(url_login, data_institution)

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

        - There's at least one association in the associations list.
        - The route can be accessed by anyone.
        - We get the same amount of associations through the model and through the view.
        - Main associations details are returned (test the "name" attribute).
        - All associations details aren't returned (test the "current_projects" attribute).
        - An association can be found with its name.
        - An association can be found with its acronym.
        - Non-enabled associations can be filtered.
        - Site associations can be filtered.
        - Associations with a specific institution ID can be filtered.
        - Associations with a specific institution component ID can be filtered.
        - Associations without a specific institution component ID can be filtered.
        - Associations with a specific institution activity field can be filtered.
        - Associations with a specific user_id cannot be filtered by an anonymous.
        - Associations with a specific user_id can be filtered by a manager.
        - Non-enabled associations can be filtered by a manager, not by student.
        - Non-public associations can be filtered by a manager, not by student.
        """
        associations_cnt = Association.objects.count()
        self.assertTrue(associations_cnt > 0)

        response = self.client.get("/associations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        association_1 = content[0]
        self.assertTrue(association_1.get("name"))
        self.assertFalse(association_1.get("current_projects"))

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

        similar_acronyms = [
            "PLANA",
            "PlanA",
            " PLANA ",
            "plan",
        ]
        for similar_acronym in similar_acronyms:
            response = self.client.get(f"/associations/?acronym={similar_acronym}")
            self.assertEqual(response.data[0]["acronym"], similar_acronyms[0])

        response = self.client.get("/associations/?is_enabled=true")
        for association in response.data:
            self.assertEqual(association["is_enabled"], True)

        response = self.client.get("/associations/?is_public=true")
        for association in response.data:
            self.assertEqual(association["is_public"], True)

        response = self.client.get("/associations/?is_site=true")
        for association in response.data:
            self.assertEqual(association["is_site"], True)

        response = self.client.get("/associations/?institution=1")
        for association in response.data:
            self.assertEqual(association["institution"]["id"], 1)

        response = self.client.get("/associations/?institution_component=1")
        for association in response.data:
            self.assertEqual(association["institution_component"], 1)

        response = self.client.get("/associations/?institution_component=")
        for association in response.data:
            self.assertEqual(association["institution_component"], None)

        response = self.client.get("/associations/?activity_field=3")
        for association in response.data:
            self.assertEqual(association["activity_field"], 3)

        response = self.client.get(f"/associations/?user_id={self.student_user_id}")
        content = json.loads(response.content.decode("utf-8"))
        links_cnt = AssociationUser.objects.filter(user_id=self.student_user_id).count()
        self.assertNotEqual(len(content), links_cnt)

        response = self.general_client.get(
            f"/associations/?user_id={self.student_user_id}"
        )
        content = json.loads(response.content.decode("utf-8"))
        links_cnt = AssociationUser.objects.filter(user_id=self.student_user_id).count()
        self.assertEqual(len(content), links_cnt)

        response = self.general_client.get("/associations/?is_enabled=false")
        for association in response.data:
            self.assertEqual(association["is_enabled"], False)

        response = self.member_client.get("/associations/?is_enabled=false")
        content = json.loads(response.content.decode("utf-8"))
        for association in response.data:
            self.assertEqual(association["is_enabled"], True)

        response = self.general_client.get("/associations/?is_public=false")
        for association in response.data:
            self.assertEqual(association["is_public"], False)

        response = self.member_client.get("/associations/?is_public=false")
        content = json.loads(response.content.decode("utf-8"))
        for association in response.data:
            self.assertEqual(association["is_public"], True)

    def test_post_association(self):
        """
        POST /associations/ .

        - Name and institution are mandatory.
        - Institution must exist.
        - A General Manager can add an association.
        - A General Manager can add a site association.
        - An Institution Manager cannot add an association not from the same institution.
        - An Institution Manager can add an association from the same institution.
        - A Misc manager cannot add an association.
        - Another user cannot add an association.
        - An association cannot be added twice, neither associations with similar names.
        - name field is mandatory.
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
            {"institution": 1000},
        )
        self.assertEqual(response_general.status_code, status.HTTP_404_NOT_FOUND)

        response_general = self.general_client.post(
            "/associations/",
            {"institution": 2},
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

        response_general = self.general_client.post(
            "/associations/",
            {"name": "Les Fans de Georges la Saucisse", "institution": 2},
        )
        self.assertEqual(response_general.status_code, status.HTTP_201_CREATED)
        non_site_association = json.loads(response_general.content.decode("utf-8"))
        self.assertFalse(non_site_association["isSite"])

        response_general = self.general_client.post(
            "/associations/",
            {
                "name": "Les gens qui savent imiter Bourvil",
                "institution": 2,
                "is_site": True,
            },
        )
        self.assertEqual(response_general.status_code, status.HTTP_201_CREATED)
        site_association = json.loads(response_general.content.decode("utf-8"))
        self.assertTrue(site_association["isSite"])
        self.assertTrue(site_association["isPublic"])

        response_institution = self.institution_client.post(
            "/associations/",
            {
                "name": "Le réalisateur de Star Wars c'est George LuCAS.",
                "institution": 2,
            },
        )
        self.assertEqual(response_institution.status_code, status.HTTP_403_FORBIDDEN)

        response_institution = self.institution_client.post(
            "/associations/",
            {
                "name": "Le plat phare du sud-ouest de la France c'est le CASsoulet.",
            },
        )
        self.assertEqual(response_institution.status_code, status.HTTP_201_CREATED)
        no_site_association = json.loads(response_institution.content.decode("utf-8"))
        self.assertFalse(no_site_association["isPublic"])
        new_association = json.loads(response_institution.content.decode("utf-8"))
        self.assertEqual(new_association["institution"], 3)

        response_misc = self.misc_client.post(
            "/associations/",
            {
                "name": "Quand Brice de Nice se connecte via CAS, c'est CASsé.",
                "institution": 2,
            },
        )
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            "/associations/",
            {
                "name": "Quelle chanteuse se connecte sans compte à l'application ? Patricia CAS",
                "institution": 2,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

        response_general = self.general_client.post("/associations/", {})
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_association_retrieve(self):
        """
        GET /associations/{id} .

        - The route can be accessed by anyone.
        - Main association details are returned (test the "name" attribute).
        - All associations details are returned (test the "current_projects" attribute).
        - A non-existing association can't be returned.
        - A non-public association can't be seen by an anonymous user.
        - A non-enabled association can't be seen by a student user who's not in it.
        - A non-public association can't be seen by a student user who's not in it.
        - A non-enabled association can be seen by a student user who's in it.
        - A non-public association can be seen by a student user who's in it.
        """
        association = Association.objects.get(pk=1)

        response = self.client.get("/associations/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        public_association = json.loads(response.content.decode("utf-8"))
        self.assertEqual(public_association["name"], association.name)
        self.assertEqual(
            public_association["currentProjects"], association.current_projects
        )

        not_found_response = self.client.get("/associations/9001")
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)

        non_public_response = self.client.get("/associations/3")
        self.assertEqual(non_public_response.status_code, status.HTTP_403_FORBIDDEN)

        non_enabled_not_member_response = self.member_client.get("/associations/5")
        self.assertEqual(
            non_enabled_not_member_response.status_code, status.HTTP_403_FORBIDDEN
        )

        non_public_not_member_response = self.member_client.get("/associations/3")
        self.assertEqual(
            non_public_not_member_response.status_code, status.HTTP_403_FORBIDDEN
        )

        non_enabled_member_response = self.member_client.get("/associations/2")
        self.assertEqual(non_enabled_member_response.status_code, status.HTTP_200_OK)

        non_public_member_response = self.member_client.get("/associations/2")
        self.assertEqual(non_public_member_response.status_code, status.HTTP_200_OK)

    def test_patch_association_authors(self):
        """
        PATCH /associations/{id} .

        - An anonymous user cannot execute this request.
        - A Misc Manager cannot edit an association.
        - A General Manager can edit an association.
        - An email is received if change is successful.
        """
        association_id = 1

        response_anonymous = self.client.patch(
            f"/associations/{association_id}",
            {"name": "La Grande Confrérie du Cassoulet de Castelnaudary"},
            content_type="application/json",
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

        response_misc = self.misc_client.patch(
            f"/associations/{association_id}",
            {"name": "L'assaucissiation"},
            content_type="application/json",
        )
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(len(mail.outbox))
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Association Amicale des Amateurs d'Andouillette Authentique",
                "institution": 1,
            },
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(
            association.name,
            "Association Amicale des Amateurs d'Andouillette Authentique",
        )
        self.assertEqual(association.institution_id, 1)
        self.assertTrue(len(mail.outbox))

    def test_patch_association_not_members(self):
        """
        PATCH /associations/{id} .

        - Someone from an association without status can't edit infos from another association.
        - Someone from an association's office cannot edit informations from another association.
        """
        association_id = 3
        response_incorrect_member = self.member_client.patch(
            f"/associations/{association_id}",
            {"name": "Je suis pas de cette asso mais je veux l'éditer."},
            content_type="application/json",
        )
        self.assertEqual(
            response_incorrect_member.status_code, status.HTTP_403_FORBIDDEN
        )
        response_incorrect_president = self.president_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Je suis membre du bureau d'une autre asso, mais je veux l'éditer."
            },
            content_type="application/json",
        )
        self.assertEqual(
            response_incorrect_president.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_patch_association_by_its_members(self):
        """
        PATCH /associations/{id} .

        - Someone from the association without status can't edit infos from the association.
        - Someone from the association's office can edit informations from the association.
        - An email is received if change is successful.
        """
        association_id = 2
        response_correct_member = self.member_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Ah et bah moi je suis de l'asso mais je peux pas l'éditer c'est terrible."
            },
            content_type="application/json",
        )
        self.assertEqual(response_correct_member.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(len(mail.outbox))
        response_correct_president = self.president_client.patch(
            f"/associations/{association_id}",
            {"name": "Moi je peux vraiment éditer l'asso, nananère."},
            content_type="application/json",
        )
        self.assertEqual(response_correct_president.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(
            association.name,
            "Moi je peux vraiment éditer l'asso, nananère.",
        )
        self.assertTrue(len(mail.outbox))

    def test_patch_association_non_existing(self):
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

    def test_patch_association_social_networks(self):
        """
        PATCH /associations/{id} .

        - A General Manager can edit an association's social networks.
        - Association's social networks are correctly updated with provided data.
        """
        association_id = 2
        social_networks_json = json.dumps(
            [{"type": "Mastodon", "location": "https://framapiaf.org/@Framasoft"}]
        )
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"social_networks": social_networks_json},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.social_networks, social_networks_json)

    def test_patch_association_wrong_social_networks(self):
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
        self.assertEqual(
            response_general_string.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_patch_association_public_or_not(self):
        """
        PATCH /associations/{id} .

        - An association can't be public if not enabled and not site.
        - An association must lost public status if enabled or site is removed.
        """
        # This association is not enabled and not site by default
        association_id = 3
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_public": True},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

        # Association public status can be true only if is_site and is_enabled are true
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": False, "is_site": True},
            content_type="application/json",
        )
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_public": True},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

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

        # Association losting its public status by changing to is_site to false
        self.general_client.patch(
            f"/associations/{association_id}",
            {"is_site": False},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

    def test_delete_association(self):
        """
        DELETE /associations/{id} .

        - An anonymous user cannot execute this request.
        - A Misc Manager cannot delete an association.
        - An enabled association cannot be deleted.
        - An Institution Manager cannot delete an association from another institution.
        - A General Manager can delete an association.
        - An email is received if deletion is successful.
        - A non-existing association cannot be deleted.
        """
        association_id = 1
        response_anonymous = self.client.delete(f"/associations/{association_id}")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        response_misc = self.misc_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)
        response_general = self.general_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_general.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(len(mail.outbox))
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": False},
            content_type="application/json",
        )
        response_institution = self.institution_client.delete(
            f"/associations/{association_id}"
        )
        self.assertEqual(response_institution.status_code, status.HTTP_403_FORBIDDEN)
        response_general = self.general_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_general.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(len(mail.outbox))
        with self.assertRaises(ObjectDoesNotExist):
            Association.objects.get(id=association_id)
        response_general = self.general_client.delete("/associations/99")
        self.assertEqual(response_general.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_association(self):
        """
        PUT /associations/{id} .

        - Request should return an error.
        """
        response = self.client.put(
            "/associations/1", {"name": "Les aficionados d'endives au jambon"}
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

        - There's at least one association name in the association names list.
        - The route can be accessed by anyone.
        - We get the same amount of associations through the model and through the view.
        - Only id and names of the associations are returned.
        - Get the same amount of associations by institution through model and view.
        - Get a different amount of associations with allow_new_users filter.
        """
        asso_names_cnt = Association.objects.count()
        self.assertTrue(asso_names_cnt > 0)

        response = self.client.get("/associations/names")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content_all_assos = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content_all_assos), asso_names_cnt)

        asso_name_1 = content_all_assos[0]
        self.assertTrue(asso_name_1.get("name"))
        self.assertTrue(asso_name_1.get("id"))
        self.assertFalse(asso_name_1.get("institution_component"))

        asso_names_cnt_institution = Association.objects.filter(
            institution_id__in=[2, 3]
        ).count()
        response = self.client.get("/associations/names?institutions=2,3")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), asso_names_cnt_institution)

        asso_names_cnt_public = Association.objects.filter(is_public=True).count()
        response = self.client.get("/associations/names?is_public=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), asso_names_cnt_public)

        AssociationUser.objects.create(user_id=12, association_id=2)

        response_assos_users_allowed = self.client.get(
            "/associations/names?allow_new_users=true"
        )
        content_assos_users_allowed = json.loads(
            response_assos_users_allowed.content.decode("utf-8")
        )
        response_assos_users_not_allowed = self.client.get(
            "/associations/names?allow_new_users=false"
        )
        content_assos_users_not_allowed = json.loads(
            response_assos_users_not_allowed.content.decode("utf-8")
        )
        self.assertEqual(
            len(content_assos_users_allowed) + len(content_assos_users_not_allowed),
            len(content_all_assos),
        )
