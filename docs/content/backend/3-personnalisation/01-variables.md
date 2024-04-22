---
title: Variables d'environnement
weight: 121
---

Plusieurs variables de l'application peuvent être customisées au déploiement distant de l'application.

## Base de données

- `default_db_host` : adresse d'accès à la base de données
- `default_db_name` : nom de la base de données
- `default_db_user` : utilisateur se connectant à la base de données
- `default_db_password` : mot de passe de la connexion à la base de données

## Stockage des fichiers S3

- `s3_endpoint` : adresse d'accès au serveur S3
- `s3_bucket` : nom du bucket de stockage des documents
- `s3_access_key` : clé d'utilisateur se connectant au serveur S3
- `s3_secret_key` : mot de passe de la connexion au serveur S3

## CAS et LDAP

- `cas_attribute_email` : nom de l'attribut CAS renvoyant l'adresse email d'un compte (`mail`)
- `cas_attribute_first_name` : nom de l'attribut CAS renvoyant le prénom d'un compte (`first_name`)
- `cas_attribute_is_student` : nom de l'attribut CAS renvoyant la valeur déterminant si le compte est celui d'un étudiant ou non (`affiliation`)
- `cas_attribute_last_name` : nom de l'attribut CAS renvoyant le nom d'un compte (`last_name`)
- `cas_authorized_services` : URLs séparées par des espaces vers lesquelles les redirections vers CAS s'effectuent (`https://etu-campulse.fr/cas-login https://etu-campulse.fr/cas-register`)
- `cas_institution_id` : identifiant en base de données de l'établissement dont les gestionnaires sont chargés de valider les comptes CAS (`2`)
- `cas_name` : nom du CAS (`CAS Unistra`)
- `cas_server` : URL du CAS (`https://cas.unistra.fr/cas/`)
- `cas_value_is_student` : valeur de l'attribut CAS déterminant si le compte est celui d'un étudiant ou non (`student`)
- `cas_version` : version du protocole CAS (`3`)
- `ldap_enabled` : True s'il est possible d'ajouter un compte côté gestionnaire via une recherche sur le LDAP (`True`)
- `accounts_api_spore_base_url` : URL d'accès au LDAP
- `accounts_api_spore_description_file` : URL d'accès au fichier JSON du LDAP
- `accounts_api_spore_token` : token d'accès au LDAP

## Serveur SMTP et envoi d'emails

- `email_host` : adresse d'accès au serveur SMTP (`127.0.0.1`)
- `email_port` : port d'accès au serveur SMTP (`25`)
- `email_host_user` : utilisateur se connectant au serveur SMTP
- `email_host_password` : mot de passe de la connexion au serveur SMTP
- `email_use_tls` : booléen définissant l'utilisation ou non du protocole TLS (`False`)
- `default_from_email` : adresse d'envoi des emails (`no-reply@unistra.fr`)
- `email_template_frontend_url` : URL d'accès à l'appli, affichée dans les mails (`https://etu-campulse.fr/`)
- `app_documentation_url` : URL d'accès à la documentation de l'appli, affichée dans les mails (`https://ernest.unistra.fr/`)

## Tâches CRON

- `cron_days_before_account_expiration_warning` : nombre de jours depuis la dernière connexion d’un compte après lequel un mail est envoyé pour prévenir de la suppression future de ce compte (`335`)
- `cron_days_before_account_expiration` : nombre de jours depuis la dernière connexion d’un compte après lequel un mail est envoyé pour prévenir de la suppression de ce compte (`365`)
- `cron_days_before_password_expiration_warning` : nombre de jours depuis le dernier changement de mot de passe d’un compte après lequel un mail est envoyé pour prévenir de l’expiration future de ce mot de passe (`335`)
- `cron_days_before_password_expiration` : nombre de jours depuis le dernier changement de mot de passe d’un compte après lequel un mail est envoyé pour prévenir de l’expiration de ce mot de passe (`365`)
- `cron_days_before_association_expiration_warning` : nombre de jours depuis la dernière mise à jour de la charte d’une association après lequel un mail est envoyé pour prévenir de l’expiration future de cette charte (`355`)
- `cron_days_before_association_expiration` : nombre de jours depuis la dernière mise à jour de la charte d’une association après lequel un mail est envoyé pour prévenir de l’expiration de cette charte (`365`)
- `cron_days_before_document_expiration_warning` : nombre de jours avant la date d’expiration d’un document après lequel un mail est envoyé pour prévenir de l’expiration future de ce document (`10`)
- `cron_days_before_review_expiration` : nombre de jours avant la date d’expiration d’un bilan après lequel un mail est envoyé pour prévenir de l’expiration future de ce bilan (`30`)
- `cron_days_before_history_expiration` : nombre de jours avant la date d’expiration d’une ligne d’historique (`90`)
- `amount_years_before_project_deletion` : nombre d'années avant qu'un projet ne soit automatiquement supprimé de la base de données (`10`)
- `amount_years_before_project_invisibility` : nombre d'années avant qu'un projet ne soit rendu invisible sur l'interface du site hors espace d'administration (`5`)

## Divers

- `migration_site_domain` : nom de domaine de l'appli (`etu-campulse.fr`)
- `migration_site_name` : nom de l'appli (`PlanA`)
- `restricted_domains` : URLs séparées par des espaces des domaines d'adresse email ne pouvant pas créer de compte local (`unistra.fr etu.unistra.fr`)
- `association_is_site_default` : booléen par défaut définissant si une association ou un fonds de commission est Site Alsace (True pour désactiver les fonctionnalités Site (`True`) Alsace)
- `association_default_amount_members_allowed` : nombre par défaut de comptes maximum pouvant se rattacher à une association (`4`)
- `new_year_month_index` : chiffre du mois à partir duquel l'année scolaire débute (utilisé pour la génération des identifiants de projets) (`9`)
