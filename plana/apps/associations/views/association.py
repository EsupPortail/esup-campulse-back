"""Views directly linked to associations."""
import datetime
import json
import unicodedata

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataReadSerializer,
    AssociationAllDataUpdateSerializer,
    AssociationMandatoryDataSerializer,
    AssociationNameSerializer,
    AssociationPartialDataSerializer,
    AssociationStatusSerializer,
)
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.users.models.user import AssociationUser
from plana.libs.mail_template.models import MailTemplate
from plana.utils import generate_pdf, send_mail, to_bool


class AssociationListCreate(generics.ListCreateAPIView):
    """/associations/ route"""

    filter_backends = [filters.SearchFilter]
    queryset = Association.objects.all().order_by("name")
    search_fields = [
        "name__nospaces__unaccent",
        "acronym__nospaces__unaccent",
        "activity_field__name__nospaces__unaccent",
        "institution__name__nospaces__unaccent",
        "institution_component__name__nospaces__unaccent",
    ]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = AssociationPartialDataSerializer
        else:
            self.serializer_class = AssociationMandatoryDataSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Association name.",
            ),
            OpenApiParameter(
                "acronym",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Association acronym.",
            ),
            OpenApiParameter(
                "is_enabled",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for non-validated associations.",
            ),
            OpenApiParameter(
                "is_public",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for associations shown in the public list.",
            ),
            OpenApiParameter(
                "is_site",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for associations from site.",
            ),
            OpenApiParameter(
                "institutions",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Institution ID.",
            ),
            OpenApiParameter(
                "institution_component",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Institution Component ID.",
            ),
            OpenApiParameter(
                "activity_field",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Activity Field ID.",
            ),
            OpenApiParameter(
                "user_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by User ID.",
            ),
        ],
        responses={
            status.HTTP_200_OK: AssociationPartialDataSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all associations with many filters."""
        name = request.query_params.get("name")
        acronym = request.query_params.get("acronym")
        is_enabled = request.query_params.get("is_enabled")
        is_public = request.query_params.get("is_public")
        is_site = request.query_params.get("is_site")
        institutions = request.query_params.get("institutions")
        institution_component = request.query_params.get("institution_component")
        activity_field = request.query_params.get("activity_field")
        user_id = request.query_params.get("user_id")

        if request.user.is_anonymous:
            is_enabled = True
            is_public = True

        if not request.user.is_anonymous and not request.user.has_perm(
            "associations.view_association_not_enabled"
        ):
            is_enabled = True

        if not request.user.is_anonymous and not request.user.has_perm(
            "associations.view_association_not_public"
        ):
            is_public = True

        if name is not None and name != "":
            name = str(name).strip()
            self.queryset = self.queryset.filter(
                name__nospaces__unaccent__icontains=name.replace(" ", "")
            )

        if acronym is not None and acronym != "":
            acronym = str(acronym).strip()
            self.queryset = self.queryset.filter(acronym__icontains=acronym)

        if is_enabled is not None and is_enabled != "":
            self.queryset = self.queryset.filter(is_enabled=to_bool(is_enabled))

        if is_public is not None and is_public != "":
            self.queryset = self.queryset.filter(is_public=to_bool(is_public))

        if is_site is not None and is_site != "":
            self.queryset = self.queryset.filter(is_site=to_bool(is_site))

        if institutions is not None and institutions != "":
            self.queryset = self.queryset.filter(
                institution_id__in=institutions.split(",")
            )

        if institution_component is not None:
            if institution_component == "":
                self.queryset = self.queryset.filter(
                    institution_component_id__isnull=True
                )
            else:
                self.queryset = self.queryset.filter(
                    institution_component_id=institution_component
                )

        if activity_field is not None and activity_field != "":
            self.queryset = self.queryset.filter(activity_field_id=activity_field)

        if (
            user_id is not None
            and user_id != ""
            and self.request.user.has_perm("users.view_user_anyone")
        ):
            self.queryset = self.queryset.filter(
                id__in=AssociationUser.objects.filter(user_id=user_id).values_list(
                    "association_id"
                )
            )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: AssociationMandatoryDataSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Creates a new association with mandatory informations (manager only)."""
        if "institution" in request.data and request.data["institution"] != "":
            try:
                Institution.objects.get(id=request.data["institution"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Institution does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if (
            not "institution" in request.data
            and request.user.get_user_managed_institutions().count() == 1
        ):
            request.data["institution"] = (
                request.user.get_user_managed_institutions().first().id
            )
        elif not "institution" in request.data:
            return response.Response(
                {"error": _("No institution given.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.has_perm(
            "associations.add_association_any_institution"
        ) and not request.user.is_staff_in_institution(request.data["institution"]):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to create an association for this institution."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "is_site" in request.data
            and to_bool(request.data["is_site"]) is True
            and not request.user.has_perm("associations.add_association_all_fields")
        ):
            return response.Response(
                {"error": _("No rights to set is_site on this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "name" not in request.data:
            return response.Response(
                {"error": _("Association name not set.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Removes spaces, uppercase and accented characters to avoid similar association names.
        new_association_name = (
            unicodedata.normalize(
                "NFD", request.data["name"].strip().replace(" ", "").lower()
            )
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        associations = Association.objects.all()
        for association in associations:
            existing_association_name = (
                unicodedata.normalize(
                    "NFD", association.name.strip().replace(" ", "").lower()
                )
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            if new_association_name == existing_association_name:
                return response.Response(
                    {"error": _("Association name already taken.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "is_site" not in request.data:
            request.data["is_site"] = settings.ASSOCIATION_IS_SITE_DEFAULT
        elif to_bool(request.data["is_site"]) is True:
            request.data["is_enabled"] = True
            request.data["is_public"] = True

        return super().create(request, *args, **kwargs)


class AssociationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/associations/{id} route"""

    queryset = Association.objects.all()

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = AssociationAllDataReadSerializer
        else:
            self.serializer_class = AssociationAllDataUpdateSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationAllDataReadSerializer,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves an association with all its details."""
        try:
            association_id = kwargs["pk"]
            association = Association.objects.get(id=association_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.is_anonymous and (
            not association.is_enabled or not association.is_public
        ):
            return response.Response(
                {"error": _("Association not visible.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            not request.user.is_anonymous
            and not association.is_enabled
            and not request.user.is_in_association(association_id)
            and not request.user.has_perm("associations.view_association_not_enabled")
        ):
            return response.Response(
                {"error": _("Association not enabled.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            not request.user.is_anonymous
            and not association.is_public
            and not request.user.is_in_association(association_id)
            and not request.user.has_perm("associations.view_association_not_public")
        ):
            return response.Response(
                {"error": _("Association not public.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # WARNING : to upload images the form sent must be "multipart/form-data" encoded
    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationAllDataUpdateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates association details (president and manager only, restricted fields for president)."""
        try:
            association_id = kwargs["pk"]
            association = Association.objects.get(id=association_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not request.user.is_president_in_association(association_id)
            and not request.user.has_perm(
                "associations.change_association_any_institution"
            )
            and not request.user.is_staff_in_institution(association.institution_id)
        ):
            return response.Response(
                {"error": _("Not allowed to edit this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            social_networks_data = (
                request.data["social_networks"]
                if "social_networks" in request.data
                else []
            )
            social_networks = (
                json.loads(social_networks_data)
                if isinstance(social_networks_data, str)
                else json.loads(json.dumps(social_networks_data))
            )
            for social_network in social_networks:
                if sorted(list(social_network.keys())) != sorted(["type", "location"]):
                    return response.Response(
                        {"error": _("Wrong social_networks parameters")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not all(isinstance(s, str) for s in list(social_network.values())):
                    return response.Response(
                        {"error": _("Wrong social_networks values")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except Exception as ex:
            print(ex)
            return response.Response(
                {"error": _("Error on social networks format.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "path_logo" in request.data
            and request.data["path_logo"] is not None
            and request.data["path_logo"].content_type
            not in settings.ALLOWED_IMAGE_MIME_TYPES
        ):
            return response.Response(
                {"error": _("Wrong media type for images.")},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
        }

        if request.user.has_perm("associations.change_association_all_fields"):
            if "amount_members_allowed" in request.data:
                amount_members_allowed = int(request.data["amount_members_allowed"])
                if (
                    amount_members_allowed
                    < AssociationUser.objects.filter(
                        association_id=association.id
                    ).count()
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Cannot set lower amount of members in this association."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if "is_public" in request.data:
                is_public = to_bool(request.data["is_public"])
                if is_public is True and (
                    association.is_site is False or association.is_enabled is False
                ):
                    request.data["is_public"] = False

            if "is_site" in request.data:
                is_site = to_bool(request.data["is_site"])
                if is_site is False:
                    request.data["is_public"] = False

            if "is_enabled" in request.data:
                is_enabled = to_bool(request.data["is_enabled"])
                if is_enabled is False:
                    request.data["is_public"] = False

            if "can_submit_projects" in request.data:
                template = None
                if to_bool(request.data["can_submit_projects"]) is False:
                    context["manager_email_address"] = request.user.email
                    template = MailTemplate.objects.get(
                        code="DEACTIVATE_PROJECT_SUBMISSION"
                    )
                elif to_bool(request.data["can_submit_projects"]) is True:
                    template = MailTemplate.objects.get(
                        code="REACTIVATE_PROJECT_SUBMISSION"
                    )
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=association.email,
                    subject=template.subject.replace(
                        "{{ site_name }}", context["site_name"]
                    ),
                    message=template.parse_vars(request.user, request, context),
                )

        else:
            for restricted_field in [
                "amount_members_allowed",
                "can_submit_projects",
                "charter_status",
                "creation_date",
                "institution_id",
                "is_enabled",
                "is_public",
                "is_site",
            ]:
                request.data.pop(restricted_field, False)

        context["first_name"] = request.user.first_name
        context["last_name"] = request.user.last_name
        context["association_name"] = association.name
        template = MailTemplate.objects.get(code="ASSOCIATION_CONTENT_CHANGE")
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=request.user.email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
        )

        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: AssociationAllDataUpdateSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def delete(self, request, *args, **kwargs):
        """Destroys an entire association (manager only)."""
        try:
            association_id = kwargs["pk"]
            association = Association.objects.get(id=association_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if association.is_enabled is True:
            return response.Response(
                {"error": _("Can't delete an enabled association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.has_perm(
            "associations.delete_association_any_institution"
        ) and not request.user.is_staff_in_institution(association.institution):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to delete an association for this institution."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if association.email:
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
            }
            template = MailTemplate.objects.get(code="ASSOCIATION_DELETE")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=association.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )
        return self.destroy(request, *args, **kwargs)


class AssociationDataExport(generics.RetrieveAPIView):
    """/associations/{id}/export route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationAllDataReadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a PDF file."""
        try:
            association = self.queryset.get(id=kwargs["pk"])
            data = association.__dict__
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("associations.view_association_not_enabled")
            and not request.user.has_perm("associations.view_association_not_public")
            and not request.user.is_president_in_association(association.id)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        data["institution"] = Institution.objects.get(
            id=association.institution_id
        ).name
        data["institution_component"] = InstitutionComponent.objects.get(
            id=association.institution_component_id
        ).name
        data["activity_field"] = ActivityField.objects.get(
            id=association.activity_field_id
        ).name

        data["documents"] = list(
            DocumentUpload.objects.filter(
                association_id=data["id"],
                document_id__in=Document.objects.filter(
                    process_type__in=["CHARTER_ASSOCIATION", "DOCUMENT_ASSOCIATION"]
                ),
            ).values("name", "document__name")
        )

        return generate_pdf(
            data, "association_charter_summary", request.build_absolute_uri("/")
        )


class AssociationNameList(generics.ListAPIView):
    """/associations/names route"""

    permission_classes = [AllowAny]
    queryset = Association.objects.all().order_by("name")
    serializer_class = AssociationNameSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "institutions",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Institutions IDs.",
            ),
            OpenApiParameter(
                "is_public",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for associations shown in the public list.",
            ),
            OpenApiParameter(
                "allow_new_users",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for associations where registration is possible.",
            ),
        ],
        responses={
            status.HTTP_200_OK: AssociationNameSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists minimal details for all associations with many filters."""
        institutions = request.query_params.get("institutions")
        is_public = request.query_params.get("is_public")
        allow_new_users = request.query_params.get("allow_new_users")
        if institutions is not None and institutions != "":
            institutions_ids = institutions.split(",")
            institutions_ids = [
                institution_id
                for institution_id in institutions_ids
                if institution_id != "" and institution_id.isdigit()
            ]
            self.queryset = self.queryset.filter(institution_id__in=institutions_ids)
        if is_public is not None and is_public != "":
            self.queryset = self.queryset.filter(is_public=to_bool(is_public))
        if allow_new_users is not None and allow_new_users != "":
            assos_ids_with_all_members = []
            for association in self.get_queryset():
                association_users = AssociationUser.objects.filter(
                    association_id=association.id
                )
                if (
                    not association.amount_members_allowed is None
                    and association_users.count() >= association.amount_members_allowed
                ):
                    assos_ids_with_all_members.append(association.id)
            if to_bool(allow_new_users) is True:
                self.queryset = self.queryset.exclude(id__in=assos_ids_with_all_members)
            else:
                self.queryset = self.queryset.filter(id__in=assos_ids_with_all_members)
        return self.list(request, *args, **kwargs)


class AssociationStatusUpdate(generics.UpdateAPIView):
    """/associations/{id}/status route"""

    queryset = Association.objects.all()
    serializer_class = AssociationStatusSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationStatusSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates association charter status."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            association = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.is_president_in_association(association.id)
            and not request.user.has_perm(
                "associations.change_association_any_institution"
            )
            and not request.user.is_staff_in_institution(association.institution_id)
        ):
            return response.Response(
                {"error": _("Not allowed to edit this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            not request.user.has_perm("associations.change_association_all_fields")
            and request.data["charter_status"] != "CHARTER_PROCESSING"
        ):
            return response.Response(
                {"error": _("Choosing this status is not allowed.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        document_process_type = "DOCUMENT_ASSOCIATION"
        missing_documents_names = (
            Document.objects.filter(
                process_type=document_process_type, is_required_in_process=True
            )
            .exclude(
                id__in=DocumentUpload.objects.filter(
                    association_id=association.id,
                ).values_list("document_id")
            )
            .values_list("name", flat=True)
        )
        if missing_documents_names.count() > 0:
            missing_documents_names_string = ', '.join(
                str(item) for item in missing_documents_names
            )
            return response.Response(
                {"error": _(f"Missing documents : {missing_documents_names_string}.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data["charter_status"] == "CHARTER_PROCESSING":
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
            }

            template = MailTemplate.objects.get(
                code="NEW_ASSOCIATION_CHARTER_TO_PROCESS"
            )
            institution = Institution.objects.get(id=association.institution_id)
            managers_emails = institution.default_institution_managers().values_list(
                "email", flat=True
            )
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=managers_emails,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

            template = MailTemplate.objects.get(code="ASSOCIATION_CHARTER_SENT")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=association.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

            request.data["charter_date"] = datetime.date.today()

        return self.update(request, *args, **kwargs)
