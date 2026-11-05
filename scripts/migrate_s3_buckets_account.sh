#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
☁️  Script de migration entre deux comptes S3

Usage :
  ./migrate_s3_buckets_content.sh \\
    --old-public old-public-bucket \\
    --old-private old-private-bucket \\
    --public new-public \\
    --private new-private \\
    --host-src s3.amazonaws.com \\
    --host-dst s3.amazonaws.com \\
    --access-src KEY1 \\
    --secret-src SECRET1 \\
    --access-dst KEY2 \\
    --secret-dst SECRET2 \\
    [--dry-run] [--no-preserve]

Options :
  --old-public         Nom du bucket public source
  --old-private        Nom du bucket privé source
  --public             Bucket destination public
  --private            Bucket destination privé
  --host-src           Endpoint S3 du compte source
  --host-dst           Endpoint S3 du compte destination
  --access-src         Access key du compte source
  --secret-src         Secret key du compte source
  --access-dst         Access key du compte destination
  --secret-dst         Secret key du compte destination
  --dry-run            Simulation sans copier réellement
  --no-preserve        Ne pas conserver les métadonnées
  --help               Afficher cette aide

Remarques :
  - Les fichiers sont d'abord téléchargés depuis le compte source
    puis envoyés vers les buckets du compte destination.
  - Toute l'arborescence est préservée automatiquement.
EOF
  exit 0
}

# Options
DRY_RUN=false
NO_PRESERVE=false

# Parsing arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --old-public) OLD_BUCKET_PUBLIC="$2"; shift 2 ;;
    --old-private) OLD_BUCKET_PRIVATE="$2"; shift 2 ;;
    --public) NEW_BUCKET_PUBLIC="$2"; shift 2 ;;
    --private) NEW_BUCKET_PRIVATE="$2"; shift 2 ;;
    --host-src) HOST_SRC="$2"; shift 2 ;;
    --host-dst) HOST_DST="$2"; shift 2 ;;
    --access-src) ACCESS_SRC="$2"; shift 2 ;;
    --secret-src) SECRET_SRC="$2"; shift 2 ;;
    --access-dst) ACCESS_DST="$2"; shift 2 ;;
    --secret-dst) SECRET_DST="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --no-preserve) NO_PRESERVE=true; shift ;;
    --help) usage ;;
    *) echo "❌ Option inconnue : $1"; exit 1 ;;
  esac
done

# Vérification des paramètres obligatoires
for var in OLD_BUCKET_PUBLIC OLD_BUCKET_PRIVATE NEW_BUCKET_PUBLIC NEW_BUCKET_PRIVATE HOST_SRC HOST_DST ACCESS_SRC SECRET_SRC ACCESS_DST SECRET_DST; do
  if [[ -z "${!var:-}" ]]; then
    echo "❌ Erreur : la variable $var est obligatoire."
    exit 1
  fi
done

# Fichiers de config temporaires
CFG_SRC=$(mktemp)
CFG_DST=$(mktemp)

cat > "$CFG_SRC" <<EOL
[default]
access_key = $ACCESS_SRC
secret_key = $SECRET_SRC
host_base = $HOST_SRC
host_bucket = %(bucket)s.$HOST_SRC
use_https = True
signature_v2 = False
EOL

cat > "$CFG_DST" <<EOL
[default]
access_key = $ACCESS_DST
secret_key = $SECRET_DST
host_base = $HOST_DST
host_bucket = %(bucket)s.$HOST_DST
use_https = True
signature_v2 = False
EOL

# Flags optionnels
EXTRA_FLAGS=""
$DRY_RUN && EXTRA_FLAGS="$EXTRA_FLAGS --dry-run"
$NO_PRESERVE && EXTRA_FLAGS="$EXTRA_FLAGS --no-preserve"

# Création des répertoires temporaires
mkdir -p /tmp/migrate_public/{logos,pdf,associations_documents_templates,associations_logos,thumbnails}
mkdir -p /tmp/migrate_private/{associations_documents,projects_notifications}

# Bucket public

echo "➡️  Migrate logos"
s3cmd --config "$CFG_SRC"  sync "s3://$OLD_BUCKET_PUBLIC/logos/" /tmp/migrate_public/logos/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_public/logos/ "s3://$NEW_BUCKET_PUBLIC/logos/" --no-mime-magic --guess-mime-type --acl-public $EXTRA_FLAGS

echo "➡️  Migrate pdf"
s3cmd --config "$CFG_SRC"  sync "s3://$OLD_BUCKET_PUBLIC/pdf/" /tmp/migrate_public/pdf/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_public/pdf/ "s3://$NEW_BUCKET_PUBLIC/pdf/" --no-mime-magic --guess-mime-type --acl-public $EXTRA_FLAGS

echo "➡️  Migrate associations documents templates"
s3cmd --config "$CFG_SRC"  sync "s3://$OLD_BUCKET_PUBLIC/associations_documents_templates/" /tmp/migrate_public/associations_documents_templates/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_public/associations_documents_templates/ "s3://$NEW_BUCKET_PUBLIC/associations_documents_templates/" --no-mime-magic --guess-mime-type --acl-public $EXTRA_FLAGS

echo "➡️  Migrate associations logos"
s3cmd --config "$CFG_SRC"  sync "s3://$OLD_BUCKET_PUBLIC/associations_logos/" /tmp/migrate_public/associations_logos/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_public/associations_logos/ "s3://$NEW_BUCKET_PUBLIC/associations_logos/" --no-mime-magic --guess-mime-type --acl-public $EXTRA_FLAGS

echo "➡️  Migrate logos thumbnails"
s3cmd --config "$CFG_SRC" sync "s3://$OLD_BUCKET_PUBLIC/thumbnails/" /tmp/migrate_public/thumbnails/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_public/thumbnails/ "s3://$NEW_BUCKET_PUBLIC/thumbnails/" --no-mime-magic --guess-mime-type --acl-public $EXTRA_FLAGS

# Bucket privé

echo "➡️  Migrate associations documents"
s3cmd --config "$CFG_SRC" sync "s3://$OLD_BUCKET_PRIVATE/associations_documents/" /tmp/migrate_private/associations_documents/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_private/associations_documents/ "s3://$NEW_BUCKET_PRIVATE/associations_documents/" --no-mime-magic --guess-mime-type --acl-private $EXTRA_FLAGS

echo "➡️  Migrate projects notifications"
s3cmd --config "$CFG_SRC" sync "s3://$OLD_BUCKET_PRIVATE/projects_notifications/" /tmp/migrate_private/projects_notifications/ $EXTRA_FLAGS
s3cmd --config "$CFG_DST" sync /tmp/migrate_private/projects_notifications/ "s3://$NEW_BUCKET_PRIVATE/projects_notifications/" --no-mime-magic --guess-mime-type --acl-private $EXTRA_FLAGS

echo "🧹 Nettoyage..."
rm -rf /tmp/migrate_public/ /tmp/migrate_private/ "$CFG_SRC" "$CFG_DST"

echo "✅ Migration terminée avec succès"
