import os
from pathlib import PosixPath

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _(
        "Generate pair of RSA 256 private and public keys to sign and verify JWT tokens"
    )

    @staticmethod
    def _key_path(key) -> PosixPath:
        return settings.SITE_ROOT / "keys" / key

    @staticmethod
    def get_confirmation(message: str) -> bool:
        answer = input(message)
        if answer.lower() in ["y", "yes", "o", "oui"]:
            return True
        return False

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-keys",
            action="store_true",
            help=_("Don't remove existing key files if they exist"),
        )

    def handle(self, *args, **options):
        private_key = self._key_path("jwt-private-key.pem")
        public_key = self._key_path("jwt-public-key.pem")
        if private_key.exists() and private_key.is_file():
            if options.get("keep_keys", False):
                self.stdout.write(self.style.NOTICE(_("Keys not replaced")))
                exit()
            if self.get_confirmation(_(f"Replace key file {str(private_key)}?")):
                private_key.unlink(missing_ok=True)
                public_key.unlink(missing_ok=True)
            else:
                raise CommandError(_("Key already exists"), returncode=1)

        cmd = f"ssh-keygen -t rsa -b 4096 -m PEM -f {str(private_key)} -N ''"
        output = os.popen(cmd)
        self.stdout.write(output.read())
        self.stdout.write(self.style.SUCCESS(_(f"Key {str(private_key)} created")))

        cmd = f"openssl rsa -in {str(private_key)} -pubout -outform PEM -out {str(public_key)}"
        output = os.popen(cmd)
        self.stdout.write(output.read())
        self.stdout.write(self.style.SUCCESS(_(f"Key {str(public_key)} created")))
