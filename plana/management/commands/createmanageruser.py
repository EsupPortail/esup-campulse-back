from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import GroupInstitutionUsers


class Command(BaseCommand):
    help = "Creates a new manager user."

    def add_arguments(self, parser):
        parser.add_argument("--email", help="Email address.", required=True)
        parser.add_argument("--firstname", help="First name.", required=True)
        parser.add_argument("--lastname", help="Last name.", required=True)
        parser.add_argument(
            "--group",
            help="Group codename.",
            choices=["MANAGER_GENERAL", "MANAGER_INSTITUTION", "MANAGER_MISC"],
            required=True,
        )
        parser.add_argument(
            "--institution",
            help="Institution codename.",
            choices=["Crous", "Unistra", "UHA", "INSA", "HEAR", "ENGEES", "ENSAS"],
        )

    def handle(self, *args, **options):
        try:
            user = get_user_model().objects.create_user(
                username=options["email"], email=options["email"]
            )
            password = get_user_model().objects.make_random_password()
            user.set_password(password)
            user.first_name = options["firstname"]
            user.last_name = options["lastname"]
            user.is_active = True
            user.is_staff = True
            user.is_validated_by_admin = True
            user.save()
            EmailAddress.objects.create(
                email=user.email, verified=True, primary=True, user_id=user.pk
            )
            group = Group.objects.get(name=options["group"])
            if options["institution"] is not None:
                institution = Institution.objects.get(acronym=options["institution"])
                GroupInstitutionUsers.objects.create(
                    user_id=user.pk, group_id=group.id, institution_id=institution.id
                )
            else:
                for institution_id in Institution.objects.values_list("id", flat=True):
                    GroupInstitutionUsers.objects.create(
                        user_id=user.pk,
                        group_id=group.id,
                        institution_id=institution_id,
                    )
            self.stdout.write(
                self.style.SUCCESS(f"User created. Password : {password}")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
