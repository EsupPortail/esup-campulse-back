"""Views directly linked to associations."""

import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as drf_filters
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.exceptions import ValidationError
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
from plana.pagination import BasePageNumberPagination
from plana.utils import send_mail

from plana.apps.associations import permissions
from plana.apps.associations.filters import AssociationFilter, AssociationNameFilter, BaseAssociationFilter
from plana.apps.users.serializers.association_user import AssociationUserSerializer


class AssociationList(generics.ListAPIView):
    """/associations/ route."""

    serializer_class = AssociationPartialDataSerializer
    filter_backends = [filters.SearchFilter, drf_filters.DjangoFilterBackend]
    pagination_class = BasePageNumberPagination
    permission_classes = [AllowAny]
    filterset_class = BaseAssociationFilter
    queryset = (
        Association.objects.filter(is_enabled=True, is_public=True)
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


class AssociationManageListCreate(generics.ListCreateAPIView):
    """/associations/manage/ route."""

    serializer_class = AssociationPartialDataSerializer
    filter_backends = [filters.SearchFilter, drf_filters.DjangoFilterBackend]
    pagination_class = BasePageNumberPagination
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
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

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = AssociationPartialDataSerializer
        else:
            self.serializer_class = AssociationMandatoryDataSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        manager_institutions = self.request.user.get_user_managed_institutions().values_list("pk")
        member_associations = self.request.user.get_user_associations().values_list("pk")
        return self.queryset.filter(
            Q(institution__in=manager_institutions) | Q(id__in=member_associations)
        ).distinct()


class AssociationRetrieve(generics.RetrieveAPIView):
    """/associations/{id} route."""

    queryset = (
        Association.objects.filter(is_enabled=True, is_public=True)
        .select_related('institution', 'institution_component', 'activity_field')
    )
    permission_classes = [AllowAny]
    serializer_class = AssociationAllDataReadSerializer


class AssociationManageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/associations/{id}/manage/ route."""

    queryset = (
        Association.objects.all()
        .select_related('institution', 'institution_component', 'activity_field')
    )
    serializer_class = AssociationAllDataReadSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, permissions.AssociationManagePermission]
    http_method_names = ["get", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = AssociationAllDataReadSerializer
        else:
            self.serializer_class = AssociationAllDataUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        manager_institutions = self.request.user.get_user_managed_institutions().values_list("pk")
        member_associations = self.request.user.get_user_associations().values_list("pk")
        return self.queryset.filter(
            Q(institution__in=manager_institutions) | Q(id__in=member_associations)
        ).distinct()

    def destroy(self, request, *args, **kwargs):
        """Custom destroy to check if the association is still enabled before deletion."""
        instance = self.get_object()
        if instance.is_enabled:
            raise ValidationError({"association_enabled": _("Can't delete an enabled association.")})
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """Custom perform_destroy to send a mail to the deleted association"""
        if instance.email:
            current_site = get_current_site(self.request)
            managers_emails = instance.institution.default_institution_managers().values_list("email", flat=True)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "manager_email_address": ",".join(managers_emails),
            }
            template = MailTemplate.objects.get(code="ASSOCIATION_ACCOUNT_DELETION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=instance.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(self.request.user, self.request, context),
            )
        super().perform_destroy(instance)


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

        serializer = self.get_serializer(instance=association, data=request.data, partial=True)
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
            charter = (
                Document.objects.filter(process_type__in=Document.ProcessType.get_charter_documents())
                .first()
            )
            if charter.expiration_day:
                if charter.expiration_day <= datetime.date.today().strftime("%m-%d"):
                    association.charter_date = datetime.datetime.strptime(
                        f"{datetime.date.today().year + 1}-{charter.expiration_day}", "%Y-%m-%d"
                    )
                else:
                    association.charter_date = datetime.datetime.strptime(
                        f"{datetime.date.today().year}-{charter.expiration_day}", "%Y-%m-%d"
                    )
            elif charter.days_before_expiration:
                association.charter_date = datetime.datetime.today() + datetime.timedelta(days=charter.days_before_expiration)
            association.save()

        mail_templates_codes_by_status = {
            "CHARTER_DRAFT_PROCESSED": "ASSOCIATION_CHARTER_REJECTION",
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


class AssociationMembersView(generics.ListAPIView):
    """
    /associations/{association_id}/users/ route.
    Used to retrieve all validated members of given association id
    Only if president of given association or association managed by auth user, or member of the association
    """

    permission_classes = [IsAuthenticated, DjangoModelPermissions, permissions.ViewAssociationMembersPermission]
    queryset = AssociationUser.objects.filter(is_validated_by_admin=True).select_related('association', 'user')
    serializer_class = AssociationUserSerializer

    def get_queryset(self):
        association_id = self.kwargs.get("association_id")
        return self.queryset.filter(association_id=association_id)
