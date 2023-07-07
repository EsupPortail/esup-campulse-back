---
title: Structure
weight: 113
---

Le dossier `plana/apps` du backend est découpé en huit sous-applications comprenant les modèles de données requis :

- `associations`
  - `association` : fiches association (logo inclus), une association doit être obligatoirement reliée à un établissement.
  - `activity_field` : domaines d'activité, une association ne peut en posséder qu'un, la liste ne peut être modifiée hors de l'interface d'administration de Django.
  - Le module comprend également un set de données de test comprenant des informations publiques sur des associations de l'Université de Strasbourg.

- `commissions`
  - `commission` : dates auxquelles auront lieu les commissions.
  - `fund` : fonds de subventionnement, un fonds doit être obligatoirement relié à un établissement, la liste ne peut être modifiée hors de l'interface d'administration de Django.
  - `commission_fund` : fonds de subventionnement représentés aux différentes dates de commissions.

- `contents`
  - `content` : contenus divers affichés sur le frontend (page d'accueil, contact, ...) et templates de PDF.
  - Le module comprend également le set de données définissant le nom initial de l'application dans la table `django_site`.

- `documents`
  - `document` : types de documents pouvant être déposés sur l'application, un document peut être relié à un fonds, les process suivants sont disponibles :
    - `CHARTER_ASSOCIATION` : charte devant être déposée par une association (exemple : Charte Site Alsace).
    - `CHARTER_PROJECT_FUND` : charte de subventionnement à renouveler pour déposer un projet (exemple : Chartes FSDIE et IdEx).
    - `DOCUMENT_ASSOCIATION` : document devant être déposé par une association pour justifier son statut (exemple : PV de l'AG constitutive).
    - `DOCUMENT_USER` : document devant être déposé par une personne pour justifier son statut (exemple : Certificat de scolarité).
    - `DOCUMENT_PROJECT` : document nécessaire à la demande de subventionnements (exemple : Budget Prévisionnel).
    - `DOCUMENT_PROJECT_REVIEW` : document nécessaire au bilan de projet (exemple : Supports de Communication).
    - `NO_PROCESS` : documents de la bibliothèque à compléter (exemples : modèles de chartes de subventionnement).
  - `document_upload` : documents envoyés par des étudiants ou des associations, liés à des projets ou non, chiffrés.

- `groups`
  - Le module ajoute des routes permettant de lire la liste des groupes et permissions accessibles dans les tables générées par Django (mais pas leur affectations aux comptes).

- `institutions`
  - `institution` : établissements, la liste ne peut être modifiée hors de l'interface d'administration de Django.
  - `institution_component` : composantes d'établissements, reliées aux établissements, la liste ne peut être modifiée hors de l'interface d'administration de Django.

- `projects`
  - `project` : demandes de subventionnements et bilans de projets, les process suivants sont disponibles :
    - `PROJECT_DRAFT` : brouillon de demande entamée.
    - `PROJECT_DRAFT_PROCESSED` : demande en cours nécessitant des modifications.
    - `PROJECT_PROCESSING` : demande en cours d'étude par les gestionnaires concernés.
    - `PROJECT_REJECTED` : demande refusée définitivement par un gestionnaire concerné.
    - `PROJECT_VALIDATED` : demande validée par l'ensemble des gestionnaires concernés.
    - `PROJECT_REVIEW_DRAFT` : brouillon de bilan attendu.
    - `PROJECT_REVIEW_PROCESSING` : bilan en cours d'étude par les gestionnaires concernés.
    - `PROJECT_REVIEW_VALIDATED` : bilan validé par un des gestionnaires concernés.
    - `PROJECT_CANCELLED` : projet validé mais finalement annulé.
  - `category` : catégories de projets, un projet peut en posséder plusieurs, la liste ne peut être modifiée hors de l'interface d'administration de Django.
  - `project_category` : catégories affectées aux différents projets.
  - `project_commission_fund` : fonds pour une commission par projet, avec les différents montants obtenus et demandés.
  - `project_comment` : commentaires laissés sur le projet par les gestionnaires.

- `users`
  - `user` : modèle utilisateur Django étendu, avec fonctions de vérification des permissions.
  - `association_user` : liens entre personnes et associations, avec les rôles dans l'association et la délégation des droits de présidence.
  - `group_institution_fund_user` : liens entre personnes, groupes, établissements et fonds.
  - Le module interagit également avec les tables `account_emailaddress`.
  - Le module gère également la connexion via un CAS et l'ajout de compte via un annuaire LDAP externe (les deux cas sont stockés dans la table `socialaccount_socialaccount`).

Le dossier `plana/libs` comporte des librairies permettant d'accéder aux données des comptes via un annuaire LDAP, et de rédiger des templates de mails dans l'interface d'administration Django.

Certaines routes provoquent la génération de fichiers PDF, leurs templates sont situés dans `plana/templates`.
