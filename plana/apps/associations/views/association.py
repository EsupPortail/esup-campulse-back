"""Views directly linked to associations."""

import datetime
import json
import unicodedata

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as drf_filters
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

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
from plana.apps.history.models.history import History
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import AssociationUser
from plana.decorators import capture_queries
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool

from .. import permissions
from ..filters import AssociationFilter, AssociationNameFilter


class AssociationListCreate(generics.ListCreateAPIView):
    """/associations/ route."""

    filter_backends = [filters.SearchFilter, drf_filters.DjangoFilterBackend]
    filterset_class = AssociationFilter
    queryset = (
        Association.objects.all()
        .select_related('institution', 'institution_component', 'activity_field')
        .order_by("name")
    )
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
        responses={
            status.HTTP_201_CREATED: AssociationMandatoryDataSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    @capture_queries()
    def post(self, request, *args, **kwargs):
        """Create a new association with mandatory informations (manager only)."""
        if "institution" in request.data and request.data["institution"] != "":
            get_object_or_404(Institution, id=request.data["institution"])

        if not "institution" in request.data and request.user.get_user_managed_institutions().count() == 1:
            request.data["institution"] = request.user.get_user_managed_institutions().first().id
        elif not "institution" in request.data:
            return response.Response(
                {"error": _("No institution given.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.has_perm(
            "associations.add_association_any_institution"
        ) and not request.user.is_staff_in_institution(request.data["institution"]):
            return response.Response(
                {"error": _("Not allowed to create an association for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "is_public" in request.data
            and to_bool(request.data["is_public"])
            and not request.user.has_perm("associations.add_association_all_fields")
        ):
            return response.Response(
                {"error": _("No rights to set is_public on this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "is_site" in request.data
            and to_bool(request.data["is_site"])
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
            unicodedata.normalize("NFD", request.data["name"].strip().replace(" ", "").lower())
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        associations = Association.objects.all()
        for association in associations:
            existing_association_name = (
                unicodedata.normalize("NFD", association.name.strip().replace(" ", "").lower())
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            if new_association_name == existing_association_name:
                return response.Response(
                    {"error": _("Association name already taken.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not "is_site" in request.data:
            request.data["is_site"] = settings.ASSOCIATION_IS_SITE_DEFAULT
        request.data["is_enabled"] = True

        return super().create(request, *args, **kwargs)


class AssociationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/associations/{id} route."""

    queryset = (
        Association.objects.all()
        .select_related('institution', 'institution_component', 'activity_field')
    )
    http_method_names = ["get", "patch", "delete"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [
                AllowAny,
                permissions.AssociationRetrieveUpdateDestroyPermission
            ]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = AssociationAllDataReadSerializer
        else:
            self.serializer_class = AssociationAllDataUpdateSerializer
        return super().get_serializer_class()

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
    @capture_queries()
    def patch(self, request, *args, **kwargs):
        """Update association details (president and manager only, restricted fields for president)."""
        association = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            not request.user.is_president_in_association(association.id)
            and not request.user.has_perm("associations.change_association_any_institution")
            and not request.user.is_staff_in_institution(association.institution_id)
        ):
            return response.Response(
                {"error": _("Not allowed to edit this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "email" in request.data and Association.objects.filter(email__iexact=request.data["email"]).exists():
            return response.Response(
                {"error": _("Email address is already used for another association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            social_networks_data = request.data["social_networks"] if "social_networks" in request.data else []
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
            return response.Response(
                {"error": _("Error on social networks format.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "path_logo" in request.data
            and request.data["path_logo"] is not None
            and request.data["path_logo"].content_type not in settings.ALLOWED_IMAGE_MIME_TYPES
        ):
            return response.Response(
                {"error": _("Wrong media type for images.")},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        current_site = get_current_site(request)
        context = {
            "site_domain": f"https://{current_site.domain}",
            "site_name": current_site.name,
        }

        if request.user.has_perm("associations.change_association_all_fields"):
            if "amount_members_allowed" in request.data:
                amount_members_allowed = int(request.data["amount_members_allowed"])
                if amount_members_allowed < AssociationUser.objects.filter(association_id=association.id).count():
                    return response.Response(
                        {"error": _("Cannot set lower amount of members in this association.")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if "is_public" in request.data:
                is_public = to_bool(request.data["is_public"])
                if is_public and not association.is_enabled:
                    request.data["is_public"] = False

            if "is_enabled" in request.data:
                is_enabled = to_bool(request.data["is_enabled"])
                if not is_enabled:
                    request.data["is_public"] = False

            if "can_submit_projects" in request.data:
                template = None
                if not to_bool(request.data["can_submit_projects"]):
                    context["manager_email_address"] = request.user.email
                    template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_SUBMISSION_DISABLED")
                elif to_bool(request.data["can_submit_projects"]):
                    template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_SUBMISSION_ENABLED")
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=association.email,
                    subject=template.subject.replace("{{ site_name }}", context["site_name"]),
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
        History.objects.create(
            action_title="ASSOCIATION_CHANGED", action_user_id=request.user.pk, association_id=association.id
        )
        template = MailTemplate.objects.get(code="USER_ACCOUNT_ASSOCIATION_CHANGE_CONFIRMATION")
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
    @capture_queries()
    def delete(self, request, *args, **kwargs):
        """Destroys an entire association (manager only)."""
        association = self.get_object()

        if association.is_enabled:
            return response.Response(
                {"error": _("Can't delete an enabled association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.has_perm(
            "associations.delete_association_any_institution"
        ) and not request.user.is_staff_in_institution(association.institution):
            return response.Response(
                {"error": _("Not allowed to delete an association for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if association.email:
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "manager_email_address": ','.join(
                    Institution.objects.get(id=association.institution_id)
                    .default_institution_managers()
                    .values_list("email", flat=True)
                ),
            }
            template = MailTemplate.objects.get(code="ASSOCIATION_ACCOUNT_DELETION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=association.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )
        return self.destroy(request, *args, **kwargs)


class AssociationNameList(generics.ListAPIView):
    """/associations/names route."""

    permission_classes = [AllowAny]
    queryset = Association.objects.all().order_by("name")
    serializer_class = AssociationNameSerializer
    filterset_class = AssociationNameFilter

    def get_queryset(self):
        return super().get_queryset().annotate(
            has_president=Exists(
                AssociationUser.objects.filter(association_id=OuterRef('pk'), is_president=True)
            )
        )


class AssociationStatusUpdate(generics.UpdateAPIView):
    """/associations/{id}/status route."""

    queryset = Association.objects.all()
    serializer_class = AssociationStatusSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    http_method_names = ["patch"]

    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationStatusSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    @capture_queries()
    def patch(self, request, *args, **kwargs):
        """Update association charter status."""
        association = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            not request.user.is_president_in_association(association.id)
            and not request.user.has_perm("associations.change_association_any_institution")
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
            Document.objects.filter(process_type=document_process_type, is_required_in_process=True)
            .exclude(
                id__in=DocumentUpload.objects.filter(
                    association_id=association.id,
                ).values_list("document_id")
            )
            .values_list("name")
        )
        if missing_documents_names.exists():
            missing_documents_names_string = ', '.join(str(item) for item in missing_documents_names)
            return response.Response(
                {"error": _(f"Missing documents : {missing_documents_names_string}.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "manager_email_address": ','.join(
                Institution.objects.get(id=association.institution_id)
                .default_institution_managers()
                .values_list("email", flat=True)
            ),
        }
        if request.data["charter_status"] == "CHARTER_PROCESSING":
            template = MailTemplate.objects.get(code="MANAGER_ASSOCIATION_CHARTER_CREATION")
            institution = Institution.objects.get(id=association.institution_id)
            managers_emails = list(institution.default_institution_managers().values_list("email", flat=True))
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=managers_emails,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )
            # TODO Very imperfect solution to get charter expiration date, please refactor when charter module will be refactored.
            charter_expiration_day = (
                Document.objects.filter(process_type__in=Document.ProcessType.get_charter_documents())
                .first()
                .expiration_day
            )
            if charter_expiration_day <= datetime.date.today().strftime("%m-%d"):
                association.charter_date = datetime.datetime.strptime(
                    f"{datetime.date.today().year + 1}-{charter_expiration_day}", "%Y-%m-%d"
                )
            else:
                association.charter_date = datetime.datetime.strptime(
                    f"{datetime.date.today().year}-{charter_expiration_day}", "%Y-%m-%d"
                )
            association.save()

        mail_templates_codes_by_status = {
            "CHARTER_DRAFT": "ASSOCIATION_CHARTER_REJECTION",
            "CHARTER_PROCESSING": "ASSOCIATION_CHARTER_CREATION",
            "CHARTER_VALIDATED": "ASSOCIATION_CHARTER_CONFIRMATION",
            "CHARTER_REJECTED": "ASSOCIATION_CHARTER_REJECTION",
        }
        if request.data["charter_status"] == "CHARTER_VALIDATED":
            association.is_site = True
            association.save()
        elif request.data["charter_status"] == "CHARTER_REJECTED":
            association.is_site = False
            association.save()
        elif request.data["charter_status"] == "CHARTER_PROCESSING":
            History.objects.create(
                action_title="ASSOCIATION_CHARTER_CHANGED",
                action_user_id=request.user.pk,
                association_id=association.id,
            )
        if request.data["charter_status"] in mail_templates_codes_by_status:
            template = MailTemplate.objects.get(code=mail_templates_codes_by_status[request.data["charter_status"]])
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=association.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        return self.update(request, *args, **kwargs)
