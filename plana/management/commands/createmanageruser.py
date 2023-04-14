import datetime

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import GroupInstitutionCommissionUser


class Command(BaseCommand):
    help = "Creates a new manager user."

    def add_arguments(self, parser):
        allowed_groups_names = []
        for group_structure_name, group_structure in settings.GROUPS_STRUCTURE.items():
            if group_structure["REGISTRATION_ALLOWED"] is False:
                allowed_groups_names.append(group_structure_name)
        group_choices = Group.objects.filter(name__in=allowed_groups_names).values_list(
            "name", flat=True
        )
        institution_choices = Institution.objects.all().values_list(
            "acronym", flat=True
        )
        parser.add_argument("--email", help="Email address.", required=True)
        parser.add_argument("--firstname", help="First name.", required=True)
        parser.add_argument("--lastname", help="Last name.", required=True)
        parser.add_argument("--password", help="Password.")
        parser.add_argument(
            "--group",
            help="Group codename.",
            choices=group_choices,
            required=True,
        )
        parser.add_argument(
            "--institution",
            help="Institution codename.",
            choices=institution_choices,
        )

    def handle(self, *args, **options):
        try:
            user = get_user_model().objects.create_user(
                username=options["email"], email=options["email"]
            )
            if options["password"] is None:
                password = get_user_model().objects.make_random_password()
            else:
                password = options["password"]
            user.set_password(password)
            user.password_last_change_date = datetime.datetime.today()
            user.first_name = options["firstname"]
            user.last_name = options["lastname"]
            user.is_active = True
            user.is_staff = True
            user.is_validated_by_admin = True
            user.save()
            EmailAddress.objects.create(
                email=user.email, verified=True, primary=True, user_id=user.id
            )
            group = Group.objects.get(name=options["group"])
            if options["institution"] is not None:
                institution = Institution.objects.get(acronym=options["institution"])
                GroupInstitutionCommissionUser.objects.create(
                    user_id=user.id, group_id=group.id, institution_id=institution.id
                )
            else:
                for institution_id in Institution.objects.values_list("id", flat=True):
                    GroupInstitutionCommissionUser.objects.create(
                        user_id=user.id,
                        group_id=group.id,
                        institution_id=institution_id,
                    )
            self.stdout.write(
                self.style.SUCCESS(f"User created. Password : {password}")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
