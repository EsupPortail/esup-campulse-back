---
title: Droits d'accès et permissions
weight: 114
---

Le projet est initialisé avec un ensemble de groupes et de permissions nivelant l'accès des différentes fonctionnalités à différents types d'utilisateurs et d'utilisatrices.

## Groupes / Rôles

Des groupes disposant de bases de permissions sont définis dans le fichier `plana/apps/groups/fixtures/auth_group.json`.

### Groupes à privilèges élevés

Ces types de groupes ne peuvent être affectés à une personne que par un administrateur avec la commande `createmanageruser`.

- `MANAGER_GENERAL` : gestionnaire général ayant accès à l'ensemble des interfaces et pouvant effectuer toutes les manipulations sur tous les établissements (exemples : gestionnaire Unistra, gestionnaire SVU, ...).
- `MANAGER_INSTITUTION` : gestionnaire d'établissement ayant accès à l'ensemble des interfaces, mais gérant uniquement les comptes et associations liées à son propre établissement (exemples : gestionnaire INSA, gestionnaire UHA, ...).
- `MANAGER_MISC` : gestionnaire d'établissement gérant également des cas particuliers (exemple : gestionnaire Crous gérant les associations hors site et étudiants porteurs de projets individuels).

Ces types de groupes doivent également être liés aux établissements concernés (la table `users_user_groups` n'est pas utilisée, les liaisons se font dans la table `users_groupinstitutioncommissionusers`).

### Groupes comportant des droits basiques

Ces types de groupes peuvent être choisis à l'inscription depuis l'application. La liste des groupes faisant partie de cette catégorie est paramétrable depuis les entrées `REGISTRATION_ALLOWED` de la variable `GROUPS_STRUCTURE` définie dans les fichiers de paramètres.

- `MEMBER_FUND` : membre de fonds (auquel lier un ou plusieurs fonds de subventionnement).
- `STUDENT_INSTITUTION` : étudiant membre d'une association en tant que président ou non (pour des raisons d'architecture, il peut être temporairement possible d'avoir ce rôle mais de n'être lié à aucune association).
- `STUDENT_MISC` : étudiant porteur de projet individuel, non membre d'une association.

Un utilisateur peut cumuler plusieurs de ces groupes, mais ne peut pas également faire partie d'un groupe à privilèges élevés.

## Permissions

L'essentiel de l'application repose sur une logique de permissions dépendant de plusieurs types de contrôles :
- des fonctions utilitaires définies dans le fichier `plana/apps/users/models/user.py` dans la classe `User` (le compte est-il relié au bon fonds, au bon établissement, à la bonne association, ...).
- des permissions Django auto-générées, ou créées manuellement dans les fichiers des modèles concernés (fichiers `plana/apps/*/models/*.py`).
- de l'appartenance à un groupe à privilèges élevés (cas spéciaux pour les routes d'ajout de données accessibles sans se connecter).

Les permissions sont à affecter uniquement à des groupes d'utilisateurs et non individuellement (la table `users_user_user_permissions` n'est pas utilisée).

## Réinitialiser les permissions des groupes et les remplacer par celles par défaut

Le développement de l'application peut régulièrement amener à créer de nouvelles permissions ou à modifier leurs affectations aux groupes, amenant à son tour à devoir modifier les données injectées par les fixtures et les dizaines d'identifiants en découlant.

Une procédure a été mise en place pour simplifier la régénération de ces fixtures en particulier (après une possible migration de la base de données), évitant ainsi d'en modifier manuellement les identifiants :
- Modifier les liens initiaux entre groupes et permissions définis dans le fichier de configuration pour ajouter/modifier/retirer les liens concernés.
- Exécuter la commande `python manage.py reset_permissions` pour supprimer tous les anciens liens entre permissions et groupes, les remplacer par les nouveaux en base de données, et régénérer les fichiers de fixtures concernés (l'argument `--flush` est également disponible pour vider la base de données et remettre les identifiants à zéro au préalable).

## Accès des associations

Les différentes fonctionnalités accordées aux associations au sein de l'application sont définies par quatre booléens de la table `associations_association`.
Les membres de groupes à privilèges élevés peuvent changer manuellement et individuellement toutes ces valeurs.

### is_enabled

Si `is_enabled` est à `true`, l'association est considérée comme active et ne peut pas être supprimée de la base de données.  
Une association est d'office considérée comme active à sa création en base de données.  
Une association inactive n'apparaît plus sur l'annuaire public et ne peut pas déposer de nouvelle demande de subventions.

### is_public

Si `is_public` est à `true`, l'association apparaît dans l'annuaire public.  
La visibilité est à définir à la création de l'association en base de données.  
Si une association devient inactive, elle devient également automatiquement non publique.

### can_submit_projects

Si `can_submit_projects` est à `true`, l'association peut déposer de nouvelles demandes de subventions.  
Une association peut d'office déposer de nouvelles demandes de subventions à sa création en base de données.  
Le paramètre est également disponible sur la table `users_user` pour gérer les cas des porteurs individuels de projets.

### is_site

Si `is_site` est à `true`, l'association est considérée comme étant Site Alsace.  
Le statut est à définir à la création de l'association en base de données. Sinon il prend la valeur du paramètre booléen `ASSOCIATION_IS_SITE_DEFAULT`.  
Si le champ `charter_status` de l'association passe à `CHARTER_VALIDATED`, l'association gagne également automatiquement le statut Site Alsace.  
Si le champ `charter_status` de l'association passe à `CHARTER_REJECTED`, l'association perd également automatiquement le statut Site Alsace.

## Accès suite au dépôt de chartes de subventionnement

Les chartes de subventionnement sont des types de documents pouvant prendre trois formes différentes.  
- `CHARTER_ASSOCIATION` : documents liés à la charte Site Alsace de l'Association.
- `CHARTER_PROJECT_FUND` : documents liés à des chartes de fonds de subventionnement à déposer périodiquement.
- `DOCUMENT_PROJECT` : documents à déposer lors de chaque demande de subventions, pouvant être liés à des chartes de fonds de subventionnement.

Les modalités d'expiration d'une charte sont définies dans un des deux champs optionnels de la table `documents_document`.
- `days_before_expiration` : durée avant expiration d'un document débutant à sa date de validation par un gestionnaire.
- `expiration_day` : date fixe de l'année (jour et mois) auxquel un document expire.

Les fonds de commissions disposent également du champ `is_site`. Par défaut, le champ prend la valeur du paramètre booléen `ASSOCIATION_IS_SITE_DEFAULT`.  
Si un fonds est défini comme étant Site Alsace, seules les associations Site Alsace peuvent lier ce fonds à leurs demandes de subventions.
Si le dépôt d'un document de charte labellisé `CHARTER_PROJECT_FUND` ou `DOCUMENT_PROJECT` est indiqué comme obligatoire, déposer ce document est requis pour lier la demande de subventions à ce fonds.
