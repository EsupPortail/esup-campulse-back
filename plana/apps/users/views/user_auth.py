"""dj-rest-auth overrided views."""

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from dj_rest_auth.registration.views import RegisterView as DJRestAutRegisterView
from dj_rest_auth.registration.views import VerifyEmailView as DJRestAuthVerifyEmailView
from dj_rest_auth.views import UserDetailsView as DJRestAuthUserDetailsView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.contents.models.setting import Setting
from plana.apps.history.models.history import History
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class PasswordResetConfirm(generics.GenericAPIView):
    """
    POST : Blank redirection to make the password reset work.

    https://dj-rest-auth.readthedocs.io/en/latest/faq.html
    """


class RegisterView(DJRestAutRegisterView):

    @transaction.atomic
    def perform_create(self, serializer):
        return super().perform_create(serializer)


@extend_schema(methods=["PUT"], exclude=True)
class UserAuthView(DJRestAuthUserDetailsView):
    """
    /users/auth/user/ route.

    Overrided UserDetailsView to prevent CAS users to change their own auto-generated fields.
    """

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        """Auto-updates user's own account."""
        if "can_submit_projects" in request.data and not self.request.user.has_perm("users.change_user_all_fields"):
            return response.Response(
                {"error": _("Only managers can edit this field.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "username" in request.data:
            return response.Response(
                {"error": _("Cannot edit this field.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        current_site = get_current_site(request)
        context = {
            "site_domain": f"https://{current_site.domain}",
            "site_name": current_site.name,
        }
        if "is_validated_by_admin" in request.data and not request.user.is_cas_user:
            request.data.pop("is_validated_by_admin", False)
        if request.user.is_cas_user:
            for restricted_field in ["email", "first_name", "last_name"]:
                if restricted_field in request.data:
                    request.data.pop(restricted_field, False)

            if not request.user.is_validated_by_admin:
                user_id = request.user.pk
                context["account_url"] = (
                    f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH}{user_id}"
                )
                History.objects.create(action_title="USER_REGISTERED", action_user_id=request.user.pk)
                template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_LDAP_CREATION")
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=request.user.get_user_default_manager_emails(),
                    subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                    message=template.parse_vars(request.user, request, context),
                )
        elif "email" in request.data:
            if request.data["email"].split('@')[1] in Setting.get_setting("RESTRICTED_DOMAINS"):
                return response.Response(
                    {"error": _("This email address cannot be used for a local account.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.data.update({"username": request.data["email"]})

        user_response = self.partial_update(request, *args, **kwargs)
        new_user_email = user_response.data["email"]
        if "email" in request.data and request.data["email"] == new_user_email:
            new_user_email_object = EmailAddress.objects.create(email=new_user_email, user_id=request.user.pk)
            context["key"] = EmailConfirmationHMAC(email_address=new_user_email_object).key
            get_adapter().send_mail(
                template_prefix="account/email/email_confirmation",
                email=new_user_email,
                context=context,
            )
        return user_response

    def delete(self, request, *args, **kwargs):
        """Auto-deletes user's own account."""
        self.permission_classes = [IsAuthenticated]
        try:
            user = self.request.user
            user.delete()
            return response.Response({}, status=status.HTTP_200_OK)
        except:
            return response.Response({}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UserAuthVerifyEmailView(DJRestAuthVerifyEmailView):
    """
    /users/auth/registration/verify-email/ route.

    OverridedVerifyEmailView to send an email to a manager (not if user revalidates an email address).
    """

    def post(self, request, *args, **kwargs):
        """Send an email to a manager on email validation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)

        user = User.objects.get(email=confirmation.email_address)
        # Important : return primary adresses first
        email_addresses = EmailAddress.objects.filter(user_id=user.id).order_by('-primary')

        if email_addresses.count() == 1:
            assos_user = AssociationUser.objects.filter(user_id=user.id)
            funds_user = GroupInstitutionFundUser.objects.filter(user_id=user.id)

            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "account_url": f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH}{user.id}",
            }
            managers_emails = user.get_user_default_manager_emails()
            History.objects.create(action_title="USER_REGISTERED", action_user_id=user.id)
            if assos_user.exists() or funds_user.exists():
                template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_LOCAL_CREATION")
            else:
                template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_LOCAL_MISC_CREATION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=managers_emails,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(user, request, context),
            )
        elif email_addresses.count() > 1:
            for email_address in email_addresses:
                if email_address.email == confirmation.email_address.email:
                    email_address.primary = True
                    email_address.save()
                else:
                    email_address.delete()
            user.username = confirmation.email_address.email
            user.save()

        return response.Response({}, status=status.HTTP_200_OK)
