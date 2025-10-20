#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<EOF
☁️  Migrate S3 buckets content
-------------------------------------
Copy content of an old S3 bucket to two new buckets (a public and a private one).

USAGE :
  ./migrate_s3_buckets_content.sh [OPTIONS]

OPTIONS :
  --old <bucket>           Name of source bucket
  --public <bucket>        Name of new public bucket
  --private <bucket>       Name of new private bucket
  --host <endpoint>     S3 endpoint (ex: s3.amazonaws.com)
  --access <key>        AWS access key
  --secret <key>        AWS secret key
  --help                Display this help message

EXAMPLE :
  ./migrate_s3_buckets_content.sh \\
    --old old-bucket \\
    --public new-public \\
    --private new-private \\
    --host s3.amazonaws.com \\
    --access \$AWS_ACCESS_KEY_ID \\
    --secret \$AWS_SECRET_ACCESS_KEY
EOF
}

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --old) OLD_BUCKET="$2"; shift 2 ;;
    --public) NEW_BUCKET_PUBLIC="$2"; shift 2 ;;
    --private) NEW_BUCKET_PRIVATE="$2"; shift 2 ;;
    --host) HOST_BASE="$2"; shift 2 ;;
    --access) S3_ACCESSKEYID="$2"; shift 2 ;;
    --secret) S3_SECRETACCESSKEY="$2"; shift 2 ;;
    --help) show_help; exit 0 ;;
    *) echo "❌ Unknown arg : $1"; echo; show_help; exit 1 ;;
  esac
done

# --- Check dependencies ---
if ! command -v s3cmd >/dev/null 2>&1; then
  echo "❌ s3cmd is not installed."
  echo "👉 Use this command before executing script : sudo apt-get install -y s3cmd"
  exit 1
fi

# --- Check parameters ---
for var in OLD_BUCKET NEW_BUCKET_PUBLIC NEW_BUCKET_PRIVATE HOST_BASE S3_ACCESSKEYID S3_SECRETACCESSKEY; do
  if [[ -z "${!var:-}" ]]; then
    echo "❌ Error : param $var is mandatory."
    echo
    show_help
    exit 1
  fi
done

# --- Tmp config for s3cmd ---
echo "☁️  Tmp config for s3cmd..."
cat > ~/.s3cfg <<EOL
[default]
access_key = "$S3_ACCESSKEYID"
secret_key = "$S3_SECRETACCESSKEY"
host_base = "$HOST_BASE"
host_bucket = "%(bucket)s.${HOST_BASE}"
signature_v2 = False
use_https = True
EOL

SRC_BUCKET="s3://$OLD_BUCKET"
PUBLIC_DEST="s3://$NEW_BUCKET_PUBLIC"
PRIVATE_DEST="s3://$NEW_BUCKET_PRIVATE"

# --- Data migrations ---
echo "🔊 Migrate public data"

echo "➡️  Migrate app logos"
s3cmd sync "$SRC_BUCKET/logos/" "$PUBLIC_DEST/logos/" --acl-public
echo "➡️  Migrate PDF templates"
s3cmd sync "$SRC_BUCKET/pdf/" "$PUBLIC_DEST/pdf/" --acl-public
echo "➡️  Migrate associations documents templates"
s3cmd sync "$SRC_BUCKET/associations_documents_templates/" "$PUBLIC_DEST/associations_documents_templates/" --acl-public
echo "➡️  Migrate associations logos"
s3cmd sync "$SRC_BUCKET/associations_logos/" "$PUBLIC_DEST/associations_logos/" --acl-public
echo "➡️  Migrate logos thumbnails"
s3cmd sync "$SRC_BUCKET/thumbnails/" "$PUBLIC_DEST/thumbnails/" --acl-public

echo "🔒️ Migrate private data"

echo "➡️  Migrate associations documents"
s3cmd sync "$SRC_BUCKET/associations_documents/" "$PRIVATE_DEST/associations_documents/" --acl-private
echo "➡️  Migrate projects notifications"
s3cmd sync "$SRC_BUCKET/projects_notifications/" "$PRIVATE_DEST/projects_notifications/" --acl-private

echo "🧹 Cleaning tmp config file..."
rm -f ~/.s3cfg

echo "✅ Migrate done."
