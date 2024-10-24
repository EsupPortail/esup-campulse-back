import os
import sys
from pathlib import PosixPath

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils.translation import gettext as _

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class Command(BaseCommand):
    help = _("Generate pair of RSA 256 private and public keys to sign and verify JWT tokens.")

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
            if options.get("keep-keys", True):
                self.stdout.write(self.style.NOTICE(_("Keys not replaced")))
                sys.exit()
            elif self.get_confirmation(_(f"Replace key file {str(private_key)}?")):
                private_key.unlink(missing_ok=True)
                public_key.unlink(missing_ok=True)
            else:
                raise CommandError(_("Key already exists"), returncode=1)

        rsa_generated_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )

        private_key.write_bytes(
            rsa_generated_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        self.stdout.write(self.style.SUCCESS(_(f"Key {str(private_key)} created")))

        public_key.write_bytes(
            rsa_generated_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
        self.stdout.write(self.style.SUCCESS(_(f"Key {str(public_key)} created")))
