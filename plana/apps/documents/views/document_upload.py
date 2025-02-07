"""Views directly linked to document uploads."""

import io
import os
import zipfile

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import FileResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.documents.serializers.document_upload import (
    DocumentUploadCreateSerializer,
    DocumentUploadFileSerializer,
    DocumentUploadListSerializer,
    DocumentUploadRetrieveSerializer,
    DocumentUploadUpdateSerializer,
)
from plana.apps.history.models.history import History
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool

from plana.decorators import capture_queries


class DocumentUploadListCreate(generics.ListCreateAPIView):
    """/documents/uploads route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = DocumentUploadCreateSerializer
        else:
            self.serializer_class = DocumentUploadListSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by User ID.",
            ),
            OpenApiParameter(
                "association_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Association ID.",
            ),
            OpenApiParameter(
                "project_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Project ID.",
            ),
            OpenApiParameter(
                "process_types",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Document process type.",
            ),
            OpenApiParameter(
                "is_validated_by_admin",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for documents not validated by an admin",
            ),
        ],
        responses={
            status.HTTP_200_OK: DocumentUploadListSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        tags=["documents/uploads"],
    )
    @capture_queries()
    def get(self, request, *args, **kwargs):
        """List all documents uploads."""
        user = request.query_params.get("user_id")
        association = request.query_params.get("association_id")
        project = request.query_params.get("project_id")
        process_types = request.query_params.get("process_types")
        is_validated_by_admin = request.query_params.get("is_validated_by_admin")

        if not request.user.has_perm("documents.view_documentupload_all"):
            user_associations_ids = AssociationUser.objects.filter(user_id=request.user.pk).values_list(
                "association_id"
            )
            user_documents_ids = DocumentUpload.objects.filter(
                models.Q(user_id=request.user.pk) | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")
            self.queryset = self.queryset.filter(id__in=user_documents_ids)

        if user is not None and user != "":
            self.queryset = self.queryset.filter(user_id=user)

        if association is not None and association != "":
            self.queryset = self.queryset.filter(association_id=association)

        if project is not None and project != "":
            self.queryset = self.queryset.filter(project_id=project)

        if process_types is not None and process_types != "":
            all_process_types = [c[0] for c in Document.process_type.field.choices]
            process_types_codes = process_types.split(",")
            process_types_codes = [
                project_type_code
                for project_type_code in process_types_codes
                if project_type_code != "" and project_type_code in all_process_types
            ]
            self.queryset = self.queryset.filter(
                document_id__in=Document.objects.filter(process_type__in=process_types_codes).values_list("id")
            )

        if is_validated_by_admin is not None and is_validated_by_admin != "":
            is_validated_by_admin = to_bool(is_validated_by_admin)
            self.queryset = self.queryset.exclude(
                validated_date__isnull=is_validated_by_admin,
            )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: DocumentUploadCreateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: None,
        },
        tags=["documents/uploads"],
    )
    def post(self, request, *args, **kwargs):
        """Create a new document upload."""
        if "document" not in request.data:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            document = Document.objects.get(id=request.data["document"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        existing_document = DocumentUpload.objects.filter(document_id=document.id)

        if request.user.is_anonymous and (
            ("association" in request.data or "project" in request.data) or document.process_type != "DOCUMENT_USER"
        ):
            return response.Response(
                {"error": _("Cannot upload documents not related to user as anonymous.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project = None
        if "project" in request.data and request.data["project"] != "":
            if document.process_type not in Document.ProcessType.get_project_documents():
                return response.Response(
                    {"error": _("Project document not allowed for this process.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                project = Project.visible_objects.get(id=request.data["project"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Project does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            existing_document = existing_document.filter(project_id=project.id)
            if not request.user.can_edit_project(project):
                return response.Response(
                    {"error": _("Not allowed to upload documents for this project.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        association = None
        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ):
            try:
                association = Association.objects.get(id=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            existing_document = existing_document.filter(association_id=association.id)
            if (
                not request.user.has_perm("documents.add_documentupload_all")
                and not request.user.is_president_in_association(request.data["association"])
                and project is None
            ):
                return response.Response(
                    {"error": _("Not allowed to post documents if not president.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        user = None
        if "user" in request.data and request.data["user"] is not None and request.data["user"] != "":
            try:
                user = User.objects.get(username=request.data["user"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("User does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            existing_document = existing_document.filter(user_id=request.user.pk)
            if (request.user.is_anonymous and user.is_validated_by_admin is True) or (
                not request.user.is_anonymous
                and not request.user.has_perm("documents.add_documentupload_all")
                and user.id != request.user.pk
            ):
                return response.Response(
                    {"error": _("Not allowed to upload documents with this user.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if "validated_date" in request.data and (
            request.user.is_anonymous or not request.user.has_perm("documents.add_documentupload_all")
        ):
            return response.Response(
                {"error": _("Not allowed to validate documents.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if association is not None and user is not None:
            return response.Response(
                {"error": _("A document upload can only have one affectation.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if association is None and user is None:
            return response.Response(
                {"error": _("No user or association specified in the new document upload.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not document.is_multiple and existing_document.exists():
            return response.Response(
                {"error": _("Document cannot be submitted multiple times.")},
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

        if request.data["path_file"].content_type not in document.mime_types:
            return response.Response(
                {"error": _("Wrong media type for this document.")},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        if document.process_type in Document.ProcessType.get_validated_documents():
            current_site = get_current_site(request)
            context = {
                "site_domain": f"https://{current_site.domain}",
                "site_name": current_site.name,
                "document_url": f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_DOCUMENT_VALIDATE_PATH}",
            }

            template = MailTemplate.objects.get(code="MANAGER_DOCUMENT_CREATION")
            managers_emails = []
            if association is not None:
                context["document_url"] += str(association.id)
                managers_emails = list(
                    Institution.objects.get(id=association.institution_id)
                    .default_institution_managers()
                    .values_list("email", flat=True)
                )
            if user is not None:
                for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                    if user_to_check.has_perm("users.change_user_misc"):
                        managers_emails.append(user_to_check.email)
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=managers_emails,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

            template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_DOCUMENT_CREATION")
            email = ""
            if association is not None:
                email = association.email
            if user is not None:
                email = user.email
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        request.data["name"] = request.data["path_file"].name
        document_upload_response = super().create(request, *args, **kwargs)
        if document.acronym == "RIB":
            History.objects.create(
                action_title="DOCUMENT_UPLOAD_CHANGED",
                action_user_id=request.user.pk,
                document_upload_id=document_upload_response.data["id"],
            )
        return document_upload_response


class DocumentUploadRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/documents/uploads/{id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = DocumentUploadUpdateSerializer
        else:
            self.serializer_class = DocumentUploadRetrieveSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentUploadRetrieveSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a document uploaded by a user."""
        try:
            document_upload = DocumentUpload.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document upload does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("documents.view_documentupload_all") and (
            (
                document_upload.project_id is not None
                and not request.user.can_access_project(Project.visible_objects.get(id=document_upload.project_id))
            )
            or (document_upload.user_id is not None and request.user.pk != document_upload.user_id)
            or (
                document_upload.association_id is not None
                and not request.user.is_in_association(document_upload.association_id)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this uploaded document.")},
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

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentUploadUpdateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
    def patch(self, request, *args, **kwargs):
        """Update document upload details."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            document_upload = self.queryset.get(id=kwargs["pk"])
            document = Document.objects.get(id=document_upload.document_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document upload does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            document.institution_id is not None
            and not request.user.has_perm("documents.change_document_any_institution")
            and not request.user.is_staff_in_institution(document.institution_id)
        ):
            return response.Response(
                {"error": _("Not allowed to update a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            document.fund_id is not None
            and not request.user.has_perm("documents.change_document_any_fund")
            and not request.user.is_member_in_fund(document.fund_id)
        ):
            return response.Response(
                {"error": _("Not allowed to update a document for this fund.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if document.acronym == "RIB":
            History.objects.create(
                action_title="DOCUMENT_UPLOAD_CHANGED",
                action_user_id=request.user.pk,
                document_upload_id=document_upload.id,
            )

        if "validated_date" in request.data and request.data["validated_date"] != "":
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
            }
            template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_DOCUMENT_CONFIRMATION")
            email = ""
            if document_upload.association_id is not None:
                email = Association.objects.get(id=document_upload.association_id).email
            if document_upload.user_id is not None:
                email = User.objects.get(id=document_upload.user_id).email
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: DocumentUploadRetrieveSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys an uploaded document."""
        try:
            document_upload = DocumentUpload.objects.get(id=kwargs["pk"])
            Document.objects.get(id=document_upload.document_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document upload does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("documents.delete_documentupload_all") and (
            (
                document_upload.project_id is not None
                and not request.user.can_edit_project(Project.visible_objects.get(id=document_upload.project_id))
            )
            or (document_upload.user_id is not None and request.user.pk != document_upload.user_id)
            or (
                document_upload.association_id is not None
                and not request.user.is_in_association(document_upload.association_id)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to delete this uploaded document.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.has_perm("documents.delete_documentupload_all"):
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
            }
            template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_DOCUMENT_REJECTION")
            managers_emails = []
            email = ""
            if document_upload.association_id is not None:
                email = Association.objects.get(id=document_upload.association_id).email
                managers_emails = list(
                    Institution.objects.get(
                        id=Association.objects.get(id=document_upload.association_id).institution_id
                    )
                    .default_institution_managers()
                    .values_list("email", flat=True)
                )
            if document_upload.user_id is not None:
                email = User.objects.get(id=document_upload.user_id).email
                for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                    if user_to_check.has_perm("users.change_user_misc"):
                        managers_emails.append(user_to_check.email)
            context["manager_email_address"] = ','.join(managers_emails)
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        return self.destroy(request, *args, **kwargs)


class DocumentUploadFileList(generics.ListAPIView):
    """/documents/uploads/file route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentUploadFileSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "project_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Project ID.",
            ),
        ],
        responses={
            status.HTTP_200_OK: DocumentUploadFileSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        tags=["documents/uploads"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all uploaded documents."""
        project = request.query_params.get("project_id")

        if project is not None and project != "":
            self.queryset = self.queryset.filter(project_id=project)

        filtered_uploads_ids = []
        for document_upload in self.get_queryset():
            if not request.user.has_perm("documents.view_documentupload_all") and (
                (
                    document_upload.project_id is not None
                    and not request.user.can_access_project(Project.visible_objects.get(id=document_upload.project_id))
                )
                or (document_upload.user_id is not None and request.user.pk != document_upload.user_id)
                or (
                    document_upload.association_id is not None
                    and not request.user.is_in_association(document_upload.association_id)
                )
            ):
                filtered_uploads_ids.append(document_upload.id)
        self.queryset = self.queryset.exclude(id__in=filtered_uploads_ids)

        buffer = io.BytesIO()
        archive = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        for document_upload in self.get_queryset():
            file = document_upload.path_file
            archive.writestr(
                os.path.basename(document_upload.path_file.name),
                bytes(file.open().read()),
            )
        archive.close()
        buffer.seek(0)

        res = HttpResponse(buffer.getvalue())
        res['Content-Type'] = "application/x-zip-compressed"
        res['Content-Disposition'] = "attachment; filename=documents.zip"

        return res


class DocumentUploadFileRetrieve(generics.RetrieveAPIView):
    """/documents/uploads/{id}/file route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentUploadFileSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentUploadFileSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a document uploaded by a user."""
        try:
            document_upload = DocumentUpload.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document upload does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("documents.view_documentupload_all") and (
            (
                document_upload.project_id is not None
                and not request.user.can_access_project(Project.visible_objects.get(id=document_upload.project_id))
            )
            or (document_upload.user_id is not None and request.user.pk != document_upload.user_id)
            or (
                document_upload.association_id is not None
                and not request.user.is_in_association(document_upload.association_id)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this uploaded document.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        file = document_upload.path_file
        return FileResponse(
            file.open(),
            as_attachment=False,
            filename=document_upload.name,
        )
