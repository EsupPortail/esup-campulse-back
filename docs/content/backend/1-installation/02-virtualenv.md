---
title: Environnement virtuel
weight: 102
---

## Gérer l'environnement virtuel avec virtualenvwrapper

- Création : `$ mkvirtualenv plana`
- Lancement : `$ workon plana`

## Variables d'environnement nécessaires

Modifier le fichier `bin/postactivate` de l'environnement virtuel dédié à l'application pour y intégrer les variables requises.

```
# Fichier de configuration `plana/settings/*.py` utilisé.
export DJANGO_SETTINGS_MODULE=plana.settings.[ENVIRONNEMENT] 

# Upload d'images et de documents sur le stockage S3.
export AWS_ACCESS_KEY_ID=AccESSkeyId
export AWS_SECRET_ACCESS_KEY=secREtaCCEsskeY
export AWS_STORAGE_BUCKET_NAME=bucket_name
export AWS_S3_ENDPOINT_URL=https://s3.domain.example

# Recherche d'un compte sur un annuaire LDAP d'université.
export ACCOUNTS_API_SPORE_DESCRIPTION_FILE="https://rest-api-domain.tld/path/description.json"
export ACCOUNTS_API_SPORE_BASE_URL="https://ldapws-domain.tld"
export ACCOUNTS_API_SPORE_TOKEN="t0k3n"
```

## Variables d'environnement au déploiement

Certaines variables doivent être reparamétrées sur les environnements de preprod et de prod.
- `SECRET_KEY` : clé utilisée par Django pour les signatures cryptographiques.
