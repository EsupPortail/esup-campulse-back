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
from plana.apps.associations.models.institution import Institution
from plana.apps.associations.models.institution_component import InstitutionComponent


class AssociationsViewsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "auth_group.json",
        "users_associationusers.json",
        "users_user.json",
        "users_user_groups.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.client = Client()
        url_login = reverse("rest_login")

        self.member_client = Client()
        data_member = {
            "username": "étudiant-asso-hors-site@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.member_client.post(url_login, data_member)

        self.president_client = Client()
        data_president = {
            "username": "président-asso-hors-site@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.president_client.post(url_login, data_president)

        self.crous_client = Client()
        data_crous = {
            "username": "gestionnaire-crous@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.crous_client.post(url_login, data_crous)

        self.svu_client = Client()
        data_svu = {
            "username": "gestionnaire-svu@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.svu_client.post(url_login, data_svu)

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
        - Associations without institution ID can be filtered.
        - Associations with a specific institution ID can be filtered.
        - Associations with a specific institution component ID can be filtered.
        - Associations with a specific institution activity field can be filtered.
        """
        associations_cnt = Association.objects.count()
        self.assertTrue(associations_cnt > 0)

        response = self.client.get("/associations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), associations_cnt)

        association_1 = content[0]
        self.assertTrue(association_1.get("name"))
        self.assertFalse(association_1.get("activities"))

        # TODO Implement unaccented search cases for names and acronyms.
        # https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/lookups/#std:fieldlookup-unaccent
        similar_names = [
            "Plateforme de Liaison et ANnuaire Associatif",
            "plateforme de liaison et annuaire associatif",
            "PlateformedeLiaisonetANnuaireAssociatif",
            "plateformedeliaisonetannuaireassociatif",
            " Plateforme de Liaison et ANnuaire Associatif ",
            # "Plàtéfôrmè dê Lîâïsön ët ANnùäire Associatif",
            "plateforme",
        ]
        for similar_name in similar_names:
            response = self.client.get(f"/associations/?name={similar_name}")
            self.assertEqual(response.data[0]["name"], similar_names[0])

        similar_acronyms = [
            "PLANA",
            "PlanA",
            " PLANA ",
            # "PLÂNÄ",
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

        response = self.client.get("/associations/?institution=")
        for association in response.data:
            self.assertEqual(association["institution"], None)

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
        - A SVU manager can add an association.
        - A Crous manager cannot add an association.
        - Another user cannot add an association.
        - An association cannot be added twice, neither associations with similar names.
        - name field is mandatory.
        """
        response_svu = self.svu_client.post(
            "/associations/",
            {
                "name": "Les Fans de Georges la Saucisse",
            },
        )
        self.assertEqual(response_svu.status_code, status.HTTP_201_CREATED)

        response_crous = self.crous_client.post(
            "/associations/",
            {
                "name": "Quand Brice de Nice se connecte via CAS, c'est CASsé.",
            },
        )
        self.assertEqual(response_crous.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            "/associations/",
            {
                "name": "Quelle chanteuse se connecte sans compte à l'application ? Patricia CAS",
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
            response_svu = self.svu_client.post(
                "/associations/",
                {"name": similar_name},
            )
            self.assertEqual(response_svu.status_code, status.HTTP_400_BAD_REQUEST)

        response_svu = self.svu_client.post("/associations/", {})
        self.assertEqual(response_svu.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_patch_association(self):
        """
        PATCH /associations/{id}
        - An anonymous user cannot execute this request.
        - A Crous manager cannot edit an association.
        - A SVU manager can edit an association.
        - An association can't be public if not enabled and not site.
        - An association must lost public status if enabled or site is removed.
        - A non-existing association cannot be edited.
        - Someone from an association without status can't edit infos from another association.
        - Someone from an association's office cannot edit informations from another association.
        - Someone from the association without status can't edit infos from the association.
        - Someone from the association's office can edit informations from the association.
        """
        association_id = 1
        response_anonymous = self.client.patch(
            f"/associations/{association_id}",
            {"name": "La Grande Confrérie du Cassoulet de Castelnaudary"},
            content_type="application/json",
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        response_crous = self.crous_client.patch(
            f"/associations/{association_id}",
            {"name": "L'assaucissiation"},
            content_type="application/json",
        )
        self.assertEqual(response_crous.status_code, status.HTTP_400_BAD_REQUEST)
        response_svu = self.svu_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Association Amicale des Amateurs d'Andouillette Authentique",
                "institution": 1,
                # TODO Find correct way to test social networks.
                # "social_networks": [
                #    {"type": "Mastodon", "location": "https://framapiaf.org/@Framasoft"}
                # ],
            },
            content_type="application/json",
        )
        self.assertEqual(response_svu.status_code, status.HTTP_200_OK)
        association = Association.objects.get(id=association_id)
        self.assertEqual(
            association.name,
            "Association Amicale des Amateurs d'Andouillette Authentique",
        )
        self.assertEqual(association.institution_id, 1)
        # self.assertEqual(len(association.social_networks), 1)

        response_svu = self.svu_client.patch(
            f"/associations/3", {"is_public": "true"}, content_type="application/json"
        )
        association = Association.objects.get(id=3)
        self.assertEqual(association.is_public, False)

        response_svu = self.svu_client.patch(
            f"/associations/3",
            {"is_enabled": "false", "is_site": "true"},
            content_type="application/json",
        )
        response_svu = self.svu_client.patch(
            f"/associations/3", {"is_public": "true"}, content_type="application/json"
        )
        association = Association.objects.get(id=3)
        self.assertEqual(association.is_public, False)
        response_svu = self.svu_client.patch(
            f"/associations/3", {"is_enabled": "true"}, content_type="application/json"
        )
        response_svu = self.svu_client.patch(
            f"/associations/3", {"is_public": "true"}, content_type="application/json"
        )
        association = Association.objects.get(id=3)
        self.assertEqual(association.is_public, True)
        response_svu = self.svu_client.patch(
            f"/associations/3", {"is_site": "false"}, content_type="application/json"
        )
        association = Association.objects.get(id=3)
        self.assertEqual(association.is_public, False)

        association_id = 99
        response_svu = self.svu_client.patch(
            f"/associations/{association_id}",
            {"name": "La singularité de l'espace-temps."},
            content_type="application/json",
        )
        self.assertEqual(response_svu.status_code, status.HTTP_400_BAD_REQUEST)

        association_id = 2
        response_incorrect_member = self.member_client.patch(
            f"/associations/{association_id}",
            {"name": "Je suis pas de cette asso mais je veux l'éditer."},
            content_type="application/json",
        )
        self.assertEqual(
            response_incorrect_member.status_code, status.HTTP_400_BAD_REQUEST
        )
        response_incorrect_president = self.president_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Je suis membre du bureau d'une autre asso, mais je veux l'éditer."
            },
            content_type="application/json",
        )
        self.assertEqual(
            response_incorrect_president.status_code, status.HTTP_400_BAD_REQUEST
        )

        association_id = 3
        response_correct_member = self.member_client.patch(
            f"/associations/{association_id}",
            {
                "name": "Ah et bah moi je suis de l'asso mais je peux pas l'éditer c'est terrible."
            },
            content_type="application/json",
        )
        self.assertEqual(
            response_correct_member.status_code, status.HTTP_400_BAD_REQUEST
        )
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

    def test_delete_association(self):
        """
        DELETE /associations/{id}
        - An anonymous user cannot execute this request.
        - A Crous manager cannot delete an association.
        - An enabled association cannot be deleted.
        - A SVU manager can delete an association.
        - A non-existing association cannot be deleted.
        """
        association_id = 1
        response_anonymous = self.client.delete(f"/associations/{association_id}")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        response_crous = self.crous_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_crous.status_code, status.HTTP_403_FORBIDDEN)
        response_svu = self.svu_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_svu.status_code, status.HTTP_400_BAD_REQUEST)
        response_svu = self.svu_client.patch(
            f"/associations/{association_id}",
            {"is_enabled": "false"},
            content_type="application/json",
        )
        response_svu = self.svu_client.delete(f"/associations/{association_id}")
        self.assertEqual(response_svu.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            Association.objects.get(id=association_id)
        response_svu = self.svu_client.delete(f"/associations/99")
        self.assertEqual(response_svu.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_get_institution_components_list(self):
        """
        GET /associations/institution_components
        - There's at least one institution component in the institution components list.
        - The route can be accessed by anyone.
        - We get the same amount of institution components through the model and through the view.
        - Institution components details are returned (test the "name" attribute).
        """
        institution_components_cnt = InstitutionComponent.objects.count()
        self.assertTrue(institution_components_cnt > 0)

        response = self.client.get("/associations/institution_components")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), institution_components_cnt)

        institution_component_1 = content[0]
        self.assertTrue(institution_component_1.get("name"))

    def test_get_institutions_list(self):
        """
        GET /associations/institutions
        - There's at least one institution in the institutions list.
        - The route can be accessed by anyone.
        - We get the same amount of institutions through the model and through the view.
        - Institutions details are returned (test the "name" attribute).
        """
        institutions_cnt = Institution.objects.count()
        self.assertTrue(institutions_cnt > 0)

        response = self.client.get("/associations/institutions")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), institutions_cnt)

        institution_1 = content[0]
        self.assertTrue(institution_1.get("name"))
