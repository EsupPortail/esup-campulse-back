---
title: Exports et notifications PDF
weight: 123
---

Les fichiers utilisés pour la génération de PDF sont externalisés dans un dépôt distinct du projet PlanA. Ils sont hébergés dans la section du bucket S3 au nom défini par la variable de configuration `S3_PDF_FILEPATH`.

Au sein de cette section, l'arborescence suivante est suggérée :
- `css` : feuilles de styles statiques appliquées aux templates
- `fonts` : polices d'écriture statiques utilisées
- `img` : images statiques (logos affichés)
- `templates/exports` : templates HTML d'exports (récap de projet, récap de charte, ...).
- `templates/notifications` : templates HTML de notifications attachées aux emails (attribution ou refus d'une aide, ...).

Les variables de configuration `TEMPLATES_PDF_EXPORTS_FOLDER` et `TEMPLATES_PDF_NOTIFICATIONS_FOLDER` permettent de modifier les chemins des deux derniers dossiers au besoin.

## Notifications d'attribution / de refus envoyées par email

Les notifications de subventions sont des fichiers PDF présents en pièces jointes des mails informant les utilisateurs d'un succès, d'un refus, ou d'un report d'une demande de subventionnement.

### Types de notifications

Ces notifications sont reliées intrinsèquement aux différents organismes de fonds qui vont traiter les demandes de subventionnement.

Nous avons ainsi 4 types de notifications, aux codes formatés comme suit :
- `NOTIFICATION_{FUND_ACRONYM}_DECISION_ATTRIBUTION` : Document présentant l'aspect légal de l'attribution de la subvention par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_ATTRIBUTION` : Document visant à prévenir les concernés que leur demande de subventionnement a été acceptée par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_REJECTION` : Document informant les concernés que leur demande de subventionnement a été refusée par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_PROJECT_POSTPONED` : Document informant les concernés que leur demande de subventionnement a été reportée à une commission future pour leur projet par le fonds désigné.

L'attribut `{FUND_ACRONYM}` ci-dessus doit obligatoirement être remplacé par l'acronyme en base de données du fonds concerné en majuscules.

Ce code est ensuite stocké dans la table `contents_content`, avec les textes des contenus qui constituent le corps du PDF de notification renvoyé.

### Variables présentes dans les contenus

Différentes variables par défaut sont présentes dans les différents contenus renvoyés et sont alors utilisables dans les différents templates de contenus.

Communes à tous les contenus : 
- `project_name` : Le nom du projet. (string)
- `date` : La date du jour à laquelle le document est généré. (date)
- `date_commission` : Date de la commission dans laquelle le projet est soumis pour le fonds désigné. (date)
- `content` : Objet Content contenant toutes les informations nécessaires au rendu du PDF de notification, il s'utilise de la manière suivante dans les templates : `{{ content.header }}` par exemple.
- `owner` : Dictionnaire contenant les informations essentielles du dépositaire du projet, c'est à dire son nom et son adresse (de l'association ou du porteur individuel de projet). Il s'utilise de la manière suivante dans les templates : `{{ owner.name }}` ou `{{ owner.address }}` selon l'information voulue.

Variables spécifiques à certains contenus uniquement : 
- `amount_earned` : Uniquement pour les notifications d'attribution, montant alloué au projet par le fonds désigné. (int)
- `comment` : Uniquement pour les notifications de refus et de report, dernier commentaire laissé sur le projet, sensé indiquer pourquoi un report ou un refus a été décidé. (string)

### Format des contenus

Les contenus sont par défaut sous format texte, cependant il est recommandé d'y ajouter des balises HTML inline (comme des `<h1>`, des `<p>` etc). A contrario, il n'est pas recommandé d'utiliser des balises block (comme des `<div>`) et de privilégier leur utilisation directement dans le template HTML au besoin.

Pour utiliser les variables ci-dessus, il suffit de les intégrer au texte de contenu sous le format `{{ var_name }}`. Elles seront alors reconnues et interprétées par le système de templating Django.

Pour chaque type de notification il n'y a qu'un seul objet Content lié, composé lui-même d'un `header`, d'un `body`, d'un `footer`, et d'un `aside` qui peuvent être utilisés pour ajouter du contenu supplémentaire au document.

Pour que l'export PDF des notifications se fasse correctement, il faut obligatoirement importer les données de Content avec la syntaxe `{% resolve %}{{ content.body|safe }}{% endresolve %}` afin de traduire le contenu du texte en HTML et d'interpréter les variables qui y sont situées.

## Exports de récapitulatifs

Les exports sont des fichiers PDF générés par l'application après une action manuelle d'un utilisateur.

### Types d'exports

Les exports sont liés à des fonctionnalités de l'application. Par défaut, les fichiers sont nommés ainsi :
- `commission_projects_list` : liste des projets rattachés à une commission.
- `association_charter_summary` : récapitulatif des données d'une association et des noms de documents déposés dans l'optique d'un renouvellement de charte.
- `project_summary` : récapitulatif du dépôt d'une demande de subventions pour un projet.
- `project_review_summary` : récapitulatif du dépôt d'un bilan d'un projet ayant été subventionné.

### Variables présentes dans les exports

#### commission_projects_list

- `name` : nom de la commission (string)
- `fields` : liste des noms des champs d'une demande de subventions (array)
- `projects` : liste des demandes de subventions (array), chaque demande contient la liste des données (array)

Champs rendus :
- Identifiant (string)
- Nom du projet (string)
- Nom de l'association (string)
- Nom et prénom de l'étudiant porteur individuel (string)
- Date de début du projet (date)
- Date de fin du projet (date)
- Est la première édition du projet (bool)
- Catégories du projet (string)

#### association_charter_summary (données d'une association)

- `name` : nom (string)
- `email` : adresse email (string)
- `acronyme` : acronyme (string)
- `social_object` : objet social (string)
- `current_projects` : projets en cours (string)
- `address` : adresse postale (string)
- `zipcode` : code postal (string)
- `city` : ville (string)
- `country` : pays (string)
- `phone` : numéro de téléphone (string)
- `siret` : numéro SIRET (string)
- `website` : site web (string)
- `student_count` : nombre d'étudiants (int)
- `charter_date` : date de dernière mise à jour de la charte (date)
- `last_goa_date` : date de la dernière assemblée générale ordinaire (date)
- `president_names` : nom et prénom de la personne présidant l'association (string)
- `president_phone` : numéro de téléphone de la personne présidant l'association (string)
- `president_email` : adresse email de la personne présidant l'association (string)
- `institution` : nom de l'établissement de rattachement (string)
- `institution_component` : nom de la composante de établissement de rattachement (string)
- `activity_field` : nom du domaine d'activité (string)
- `documents` : liste des documents (array), chaque document contient ces propriétés (object) :
  - `document__name` : nom du document de base (string)
  - `name` : nom donné au fichier (string)

#### project_summary et project_review_summary (données d'une demande de subventions pour un projet)

- `name` : nom (string)
- `manual_identifier` : identifiant généré (string)
- `planned_start_date` : date prévue de début (date)
- `planned_end_date` : date prévue de fin (date)
- `planned_location` : lieu prévu (date)
- `partner_association` : nom de l'association co-organisatrice (string)
- `budget_previous_edition` : budget de l'édition précédente (int) 
- `target_audience` : public visé (string)
- `amount_students_audience` : nombre de personnes attendues dans le public étudiant (int)
- `amount_all_audience` : nombre de personnes attendues au total (int)
- `ticket_price` : prix d'entrée (int)
- `student_ticket_price` : prix d'entrée pour le public étudiant (int)
- `individual_cost` : coût du projet par personne attendue (int)
- `goals` : objectifs (string)
- `summary` : résumé (string)
- `planned_activities` : activités prévues (string)
- `prevention_safety` : actions de prévention et de sécurité prévues (string)
- `marketing_campaign` : campagne de communication (string)
- `sustainable_development` : actions en faveur du Développement Durable et de la Responsabilité Sociétale (string)
- `processing_date` : date de dépôt du projet (date)
- `outcome` : dépenses (int)
- `income` : recettes (int)
- `real_start_date` : date réelle de début (date)
- `real_end_date` : date réelle de fin (date)
- `real_location` : lieu réel (date)
- `review` : bilan (string)
- `impact_students` : impact sur la population étudiante (string)
- `description` : description, activités réalisées, changements par rapport au planning (string)
- `difficulties` : difficultés rencontrées (string)
- `improvements` : améliorations possibles (string)
- `is_first_edition` : est la première édition du projet (bool)
- `commission_name` : nom de la commission (string)
- `commission_date` : date du déroulé physique de la commission (date)
- `categories` : liste de toutes les catégories (array), chaque catégorie contient ces propriétés (object) :
  - `id` : identifiant (int)
  - `name` : nom (string)
- `project_categories` : liste (array) de tous les identifiants de catégories liés à la demande (int).
- `project_commission_funds` : liste de tous les fonds liés à une demande (array), chaque fonds contient ces propriétés (object) :
  - `commission_fund_id` : identifiant (int)
  - `is_first_edition` : est la première édition du projet (bool)
  - `amount_asked_previous_edition` : montant demandé à la précédente édition du projet (int)
  - `amount_earned_previous_edition` : montant reçu à la précédente édition du projet (int)
  - `amount_asked` : montant demandé (int)
  - `amount_earned` : montant reçu (int)
  - `commission_data` : données de la commission (object) :
    - `name` : nom (string)
    - `submission_date` : date de clôture de la soumission de nouvelles demandes (date)
    - `commission_date` : date du déroulé physique de la commission (date)
  - `fund_data` : données du fonds (object) :
    - `name` : nom (string)
    - `acronym` : acronyme (string)
- `association` : données de l'association (object) :
  - `name` : nom (string)
  - `email` : adresse email (string)
  - `acronyme` : acronyme (string)
  - `social_object` : objet social (string)
  - `current_projects` : projets en cours (string)
  - `address` : adresse postale (string)
  - `zipcode` : code postal (string)
  - `city` : ville (string)
  - `country` : pays (string)
  - `phone` : numéro de téléphone (string)
  - `siret` : numéro SIRET (string)
  - `website` : site web (string)
  - `student_count` : nombre d'étudiants (int)
  - `charter_date` : date de dernière mise à jour de la charte (date)
  - `last_goa_date` : date de la dernière assemblée générale ordinaire (date)
  - `president_names` : nom et prénom de la personne présidant l'association (string)
  - `president_phone` : numéro de téléphone de la personne présidant l'association (string)
  - `president_email` : adresse email de la personne présidant l'association (string)
- `user` : données du responsable de projet dans l'association ou du porteur individuel (object) :
  - `email` : adresse email (string)
  - `first_name` : prénom (string)
  - `last_name` : nom de famille (string)
  - `address` : adresse postale (string)
  - `zipcode` : code postal (string)
  - `city` : ville (string)
  - `country` : pays (string)
  - `phone` : numéro de téléphone (string)
- `documents` : liste des documents (array), chaque document contient ces propriétés (object) :
  - `document__name` : nom du document de base (string)
  - `name` : nom donné au fichier (string)
