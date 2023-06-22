---
title: Variables Django
weight: 104
---

Les fichiers situés dans `plana/settings` comportent des variables paramétrant le comportement de l'application.

## Authentification via CAS

Plusieurs variables permettent d'intégrer le serveur CAS pour authentifier des comptes universitaires :
- `CAS_SERVER` : URL du serveur CAS.
- `CAS_AUTHORIZED_SERVICES` : URLs des clients frontend autorisées à communiquer avec le serveur pour valider les tickets.

## Stockage

Le stockage des fichiers est optimisé pour un serveur S3 découpé en trois buckets :
- `S3_LOGO_FILEPATH` : nom du bucket pour stocker les logos des associations (voir modèle `Association`).
- `S3_TEMPLATES_FILEPATH` : nom du bucket pour stocker les modèles de documents publics (voir modèle `Document`).
- `S3_DOCUMENTS_FILEPATH` : nom du cucket pour stocker les documents des étudiantes et étudiants de manière chiffrée (voir modèle `DocumentUpload`).

## Logos des associations

Les logos des associations sont convertis en miniatures de différentes tailles leur import avec l'aide du module [`django-thumbnails`](https://github.com/ui/django-thumbnails).
- `THUMBNAILS` : objet comprenant la configuration du module.
- `THUMBNAILS.SIZES` : liste des tailles proposées :
  - `list` : taille réduite pour la page de la liste des associations.
  - `detail` : taille plus élevée pour la page de détail d'une association.
  - `base` : taille maximale du fichier.

## Variables intégrées dans les templates de mails

Certains emails renvoyés par l'API intègrent des liens menant à des pages du frontend. Leurs chemins peuvent être personnalisés.

- `MIGRATION_SITE_DOMAIN` : domaine de base du frontend (utilisé dans la table `django_site`).
- `MIGRATION_SITE_NAME` : nom de l'application (utilisé dans la table `django_site`).
- `EMAIL_TEMPLATE_FRONTEND_URL` : URL de base du frontend.
- `EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_URL` : chemin menant à la page de vérification de l'adresse mail à l'inscription.
- `EMAIL_TEMPLATE_PASSWORD_RESET_URL` : chemin menant à la page de réinitialisation du mot de passe pour une personne non connectée.
- `EMAIL_TEMPLATE_PASSWORD_CHANGE_URL` : chemin menant à la page de changement du mot de passe pour une personne connectée.
- `EMAIL_TEMPLATE_ACCOUNT_VALIDATE_URL` : chemin menant à la page de validation des comptes pour un gestionnaire connecté.
- `APP_DOCUMENTATION_URL` : URL menant vers la documentation utilisateur.

## Autres variables

- `DEFAULT_FROM_EMAIL` : adresse mail "noreply" par défaut renseignée dans les emails envoyés par l'appli.
- `RESTRICTED_DOMAINS` = domaines d'adresses mail non autorisés à créer des comptes locaux (généralement, les domaines utilisés par les comptes CAS).
- `ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED` : nombre de comptes autorisés à se relier à une association.
- `ASSOCIATION_IS_SITE_DEFAULT` : définit un degré de validation supplémentaire pour accéder à l'ensemble des fonctionnalités côté association (utilisé pour la Charte Site Alsace par exemple), laisser à `True` pour désactiver la vérification.
- `AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY` : nombre d'années durant lesquelles un projet est visible dans l'application (avant d'être réservé à l'interface d'administration).
- `AMOUNT_YEARS_BEFORE_PROJECT_DELETION` : nombre d'années durant lesquelles un projet est stocké dans l'application (avant d'être supprimé).
