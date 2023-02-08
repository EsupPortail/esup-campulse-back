"""
List of tests done on associations views.
"""
import json

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association


class AssociationsViewsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationusers.json",
        "users_user.json",
        "users_groupinstitutionusers.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.client = Client()
        url_login = reverse("rest_login")

        self.student_user_id = 11
        self.student_user_name = "etudiant-asso-site@mail.tld"
        self.member_client = Client()
        data_member = {
            "username": self.student_user_name,
            "password": "motdepasse",
        }
        self.response = self.member_client.post(url_login, data_member)

        self.president_user_id = 13
        self.president_user_name = "president-asso-site@mail.tld"
        self.president_client = Client()
        data_president = {
            "username": self.president_user_name,
            "password": "motdepasse",
        }
        self.response = self.president_client.post(url_login, data_president)

        self.manager_misc_user_id = 5
        self.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        self.misc_client = Client()
        data_misc = {
            "username": self.manager_misc_user_name,
            "password": "motdepasse",
        }
        self.response = self.misc_client.post(url_login, data_misc)

        self.manager_institution_user_id = 4
        self.manager_institution_user_name = "gestionnaire-uha@mail.tld"
        self.institution_client = Client()
        data_institution = {
            "username": self.manager_institution_user_name,
            "password": "motdepasse",
        }
        self.response = self.institution_client.post(url_login, data_institution)

        self.manager_general_user_id = 3
        self.manager_general_user_name = "gestionnaire-svu@mail.tld"
        self.general_client = Client()
        data_general = {
            "username": self.manager_general_user_name,
            "password": "motdepasse",
        }
        self.response = self.general_client.post(url_login, data_general)

    def test_get_associations_list(self):
        """
        GET /associations/
        - There's at least one association in the associations list.
        - The route can be accessed by anyone.
        - We get the same amount of associations through the model and through the view.
        - Main associations details are returned (test the "name" attribute).
        - All associations details aren't returned (test the "activities" attribute).
        - An association can be found with its name.
        - An association can be found with its acronym.
        - Non-enabled associations can be filtered.
        - Site associations can be filtered.
        - Associations without institution component ID can be filtered.
        - Associations with a specific institution ID can be filtered.
        - Associations with a specific institution component ID can be filtered.
        - Associations with a specific institution activity field can be filtered.
        """
        associations_cnt = Association.objects.count()
        self.assertTrue(associations_cnt > 0)

        response = self.client.get("/associations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        association_1 = content[0]
        self.assertTrue(association_1.get("name"))
        self.assertFalse(association_1.get("activities"))

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

        response = self.client.get("/associations/?institution_component=")
        for association in response.data:
            self.assertEqual(association["institution_component"], None)

        response = self.client.get("/associations/?institution=1")
        for association in response.data:
            self.assertEqual(association["institution"]["id"], 1)

        response = self.client.get("/associations/?institution_component=1")
        for association in response.data:
            self.assertEqual(association["institution_component"]["id"], 1)

        response = self.client.get("/associations/?activity_field=3")
        for association in response.data:
            self.assertEqual(association["activity_field"]["id"], 3)

    def test_post_association(self):
        """
        POST /associations/
        - Name and institution are mandatory.
        - A General Manager can add an association.
        - An Institution manager cannot add an association.
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
            {"institution": 2},
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

        response_general = self.general_client.post(
            "/associations/",
            {"name": "Les Fans de Georges la Saucisse", "institution": 2},
        )
        self.assertEqual(response_general.status_code, status.HTTP_201_CREATED)

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
        GET /associations/{id}
        - The route can be accessed by anyone.
        - Main association details are returned (test the "name" attribute).
        - All associations details are returned (test the "activities" attribute).
        - A non-existing association can't be returned.
        """
        association = Association.objects.get(pk=1)

        response = self.client.get("/associations/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        association_1 = json.loads(response.content.decode("utf-8"))
        self.assertEqual(association_1["name"], association.name)
        self.assertEqual(association_1["activities"], association.activities)

        not_found_response = self.client.get("/associations/50")
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_association_authors(self):
        """
        PATCH /associations/{id}
        - An anonymous user cannot execute this request.
        - A Misc Manager cannot edit an association.
        - A General Manager can edit an association.
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

    def test_patch_association_not_members(self):
        """
        PATCH /associations/{id}
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
        PATCH /associations/{id}
        - Someone from the association without status can't edit infos from the association.
        - Someone from the association's office can edit informations from the association.
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

    def test_patch_association_non_existing(self):
        """
        PATCH /associations/{id}
        - A non-existing association cannot be edited.
        """
        association_id = 99
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"name": "La singularité de l'espace-temps."},
            content_type="application/json",
        )
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_association_social_networks(self):
        """
        PATCH /associations/{id}
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
        PATCH /associations/{id}
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
        PATCH /associations/{id}
        - An association can't be public if not enabled and not site.
        - An association must lost public status if enabled or site is removed.
        """
        # This association is not enabled and not site by default
        association_id = 3
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_public": True},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

        # Association public status can be true only if is_site and is_enabled are true
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": False, "is_site": True},
            content_type="application/json",
        )
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_public": True},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": True},
            content_type="application/json",
        )
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_public": True},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, True)

        # Association losting its public status by changing to is_site to false
        response_general = self.general_client.patch(
            f"/associations/{association_id}",
            {"is_site": False},
            content_type="application/json",
        )
        association = Association.objects.get(id=association_id)
        self.assertEqual(association.is_public, False)

    def test_delete_association(self):
        """
        DELETE /associations/{id}
        - An anonymous user cannot execute this request.
        - A Misc Manager cannot delete an association.
        - An enabled association cannot be deleted.
        - An Institution Manager cannot delete an association from another institution.
        - A General Manager can delete an association.
        - A non-existing association cannot be deleted.
        """
        association_id = 1
        response_anonymous = self.client.delete(f"/associations/{association_id}")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        response_misc = self.misc_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_misc.status_code, status.HTTP_403_FORBIDDEN)
        response_general = self.general_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_general.status_code, status.HTTP_403_FORBIDDEN)
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
        with self.assertRaises(ObjectDoesNotExist):
            Association.objects.get(id=association_id)
        response_general = self.general_client.delete("/associations/99")
        self.assertEqual(response_general.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_association(self):
        """
        PUT /associations/{id}
        - Request should return an error.
        """
        response = self.client.put(
            "/associations/1", {"name": "Les aficionados d'endives au jambon"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_activity_fields_list(self):
        """
        GET /associations/activity_fields
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
