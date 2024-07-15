---
title: Variables Django
weight: 104
---

Les fichiers situés dans `plana/settings` comportent des variables paramétrant le comportement de l'application selon l'environnement utilisé.  
Certaines de ces variables doivent être paramétrées différemment pour le déploiement distant (voir section `Personnalisation`).  
D'autres variables non critiques sont accessibles via la table `contents_setting`.

## Authentification via CAS

Plusieurs variables permettent d'intégrer le serveur CAS pour authentifier des comptes universitaires :
- `CAS_NAME` : nom du serveur CAS.
- `CAS_SERVER` : URL du serveur CAS.
- `CAS_VERSION` : version du service CAS.
- `CAS_AUTHORIZED_SERVICES` : URLs des clients frontend autorisées à communiquer avec le serveur pour valider les tickets.
- `CAS_ATTRIBUTES_NAMES`: clés-valeurs des champs de la table User correspondant aux noms des champs envoyés par CAS.
- `CAS_ATTRIBUTES_VALUES`: clés-valeurs des champs de la table User correspondant aux valeurs des champs envoyés par CAS.

## Stockage

Le stockage des fichiers est optimisé pour un bucket S3 découpé en cinq sections :
- `S3_LOGOS_FILEPATH` : nom de la section pour stocker les logos du footer (voir modèle `Logo`).
- `S3_ASSOCIATIONS_LOGOS_FILEPATH` : nom de la section pour stocker les logos des associations (voir modèle `Association`).
- `S3_TEMPLATES_FILEPATH` : nom de la section pour stocker les modèles de documents publics (voir modèle `Document`).
- `S3_DOCUMENTS_FILEPATH` : nom de la section pour stocker les documents des étudiantes et étudiants de manière chiffrée (voir modèle `DocumentUpload`).
- `S3_PDF_FILEPATH` : nom de la section pour stocker les fichiers liés à la génération des PDF des notifications et exports (pas de modèle).

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
- `EMAIL_TEMPLATE_ACCOUNT_VALIDATE_URL` : chemin menant à la page de validation d'une charte pour un gestionnaire connecté.

## Autres variables

- `DEFAULT_PASSWORD_LENGTH` : taille des mots de passe générés.
- `DEFAULT_FROM_EMAIL` : adresse mail "noreply" par défaut renseignée dans les emails envoyés par l'appli.
- `LDAP_ENABLED` : active ou non la possibilité d'ajouter des comptes via un annuaire LDAP.
- `ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED` : nombre de comptes autorisés à se relier à une même association.
- `ASSOCIATION_IS_SITE_DEFAULT` : définit un degré de validation supplémentaire pour accéder à l'ensemble des fonctionnalités de l'application côté association (utilisé pour définir si une association a signé la Charte Site Alsace de l'Université de Strasbourg par exemple), laisser à `True` pour désactiver la validation.
