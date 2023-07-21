---
title: Variables Django
weight: 104
---

Les fichiers situés dans `plana/settings` comportent des variables paramétrant le comportement de l'application selon l'environnement utilisé.

## Authentification via CAS

Plusieurs variables permettent d'intégrer le serveur CAS pour authentifier des comptes universitaires :
- `CAS_SERVER` : URL du serveur CAS.
- `CAS_AUTHORIZED_SERVICES` : URLs des clients frontend autorisées à communiquer avec le serveur pour valider les tickets.

## Stockage

Le stockage des fichiers est optimisé pour un serveur S3 découpé en trois buckets :
- `LOGO_FILEPATH` : nom du bucket pour stocker les logos des associations (voir modèle `Association`).
- `TEMPLATES_FILEPATH` : nom du bucket pour stocker les modèles de documents publics (voir modèle `Document`).
- `DOCUMENTS_FILEPATH` : nom du bucket pour stocker les documents des étudiantes et étudiants de manière chiffrée (voir modèle `DocumentUpload`).

## Logos des associations

Les logos des associations sont convertis en miniatures de différentes tailles leur import avec l'aide du module [`django-thumbnails`](https://github.com/ui/django-thumbnails).
- `THUMBNAILS` : objet comprenant la configuration du module.
- `THUMBNAILS.SIZES` : liste des tailles proposées :
  - `list` : taille réduite pour la page de la liste des associations.
  - `detail` : taille plus élevée pour la page de détail d'une association.
  - `base` : taille maximale du fichier (le fichier original n'est pas conservé mais stocké avec cette taille).

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

## Nombre de jours attendus dans les tâches CRON.

Les tâches CRON envoient de multiples emails dont des relances dépendant de nombres de jours.
- `CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION_WARNING` : nombre de jours depuis la dernière connexion d'un compte après lequel un mail est envoyé pour prévenir de la suppression future de ce compte.
- `CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION` :  : nombre de jours depuis la dernière connexion d'un compte après lequel un mail est envoyé pour prévenir de la suppression de ce compte.
- `CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION_WARNING` : nombre de jours depuis la dernière mise à jour de la charte d'une association après lequel un mail est envoyé pour prévenir de l'expiration future de cette charte.
- `CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION ` : : nombre de jours depuis la dernière mise à jour de la charte d'une association après lequel un mail est envoyé pour prévenir de l'expiration de cette charte.
- `CRON_DAYS_DELAY_BEFORE_DOCUMENT_EXPIRATION_WARNING` : nombre de jours avant la date d'expiration d'un document après lequel un mail est envoyé pour prévenir de l'expiration future de ce document.
- `CRON_DAYS_BEFORE_PASSWORD_EXPIRATION_WARNING` : nombre de jours depuis le dernier changement de mot de passe d'un compte après lequel un mail est envoyé pour prévenir de l'expiration future de ce mot de passe.
- `CRON_DAYS_BEFORE_PASSWORD_EXPIRATION` : nombre de jours depuis le dernier changement de mot de passe d'un compte après lequel un mail est envoyé pour prévenir de l'expiration de ce mot de passe.
- `CRON_DAYS_DELAY_AFTER_REVIEW_EXPIRATION` : nombre de jours avant la date d'expiration d'un bilan après lequel un mail est envoyé pour prévenir de l'expiration future de ce bilan.

## Autres variables

- `DEFAULT_PASSWORD_LENGTH` : taille des mots de passe générés.
- `DEFAULT_FROM_EMAIL` : adresse mail "noreply" par défaut renseignée dans les emails envoyés par l'appli.
- `RESTRICTED_DOMAINS` : domaines d'adresses mail non autorisés pour les comptes locaux (généralement, les domaines utilisés par les comptes se connectant via le CAS paramétré).
- `ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED` : nombre de comptes autorisés à se relier à une même association.
- `ASSOCIATION_IS_SITE_DEFAULT` : définit un degré de validation supplémentaire pour accéder à l'ensemble des fonctionnalités de l'application côté association (utilisé pour définir si une association a signé la Charte Site Alsace de l'Université de Strasbourg par exemple), laisser à `True` pour désactiver la validation.
- `NEW_YEAR_MONTH_INDEX` : index du mois auquel une année scolaire débute (9 pour Septembre).
- `AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY` : nombre d'années durant lesquelles un projet est visible dans l'application (avant d'être uniquement visible sur l'interface d'administration de Django).
- `AMOUNT_YEARS_BEFORE_PROJECT_DELETION` : nombre d'années durant lesquelles un projet est stocké dans l'application (avant d'être supprimé).
