---
title: Droits
weight: 25
pre: "<b>5. </b>"
---

## Créer un utilisateur gestionnaire

Pout créer un nouvel utilisateur gestionnaire au sein de l'application, il existe deux méthodes : 
- Via l'interface Django-Admin en créant les entrées nécessaires (user, adresse mail, validation, ...)
- Via la ligne de commande

Pour créer un utilisateur gestionnaire, il faut lancer la commande suivante à la racine du projet : 

```
$ python manage.py createmanageruser --email EMAIL --firstname FIRST_NAME --lastname LAST_NAME --group GROUP_NAME [--institution INSTITUTION]
```

Si aucune institution n'est spécifiée, le gestionnaire créé aura accès à toutes les institutions.

## Rôles et permissions par défaut

Le projet est initialisé avec un ensemble de groupes et de permissions nivelant l'accès des différentes fonctionnalités à différents types d'utilisateurs et d'utilisatrices.

### Groupes / Rôles

Des groupes disposant de bases de permissions sont définis dans le fichier `plana/apps/groups/fixtures/auth_group.json`.

#### Groupes à privilèges élevés

Ces types de groupes ne peuvent être affectés que par un administrateur au travers des procédures citées sur la page.

- `MANAGER_GENERAL` : gestionnaire général ayant accès à l'ensemble des interfaces et pouvant effectuer toutes les manipulations sur tous les établissements (exemples : gestionnaire Unistra, gestionnaire SVU, ...).
- `MANAGER_INSTITUTION` : gestionnaire d'établissement ayant accès à l'ensemble des interfaces, mais gérant uniquement les comptes et associations liées à son propre établissement (exemples : gestionnaire INSA, gestionnaire UHA, ...).
- `MANAGER_MISC` : gestionnaire d'établissement gérant également des cas particuliers (exemple : gestionnaire Crous gérant les associations hors site et étudiants porteurs de projets individuels).

Ces types de groupes doivent également être liés aux établissements concernés (la table `users_user_groups` n'est pas utilisée, les liaisons se font dans la table `users_groupinstitutioncommissionusers`).

#### Groupes comportant des droits basiques

Ces types de groupes peuvent être choisis à l'inscription depuis l'application. La liste des groupes faisant partie de cette catégorie est paramétrable depuis les entrées `REGISTRATION_ALLOWED` de la variable `GROUPS_STRUCTURE` définie dans le fichier `plana/settings/base.py`.

- `COMMISSION` : membre de commission (auquel lier une ou plusieurs commissions).
- `STUDENT_INSTITUTION` : étudiant membre d'une association en tant que président ou non (pour des raisons d'architecture, il peut être temporairement possible d'avoir ce rôle mais de n'être lié à aucune association).
- `STUDENT_MISC` : étudiant porteur de projet individuel, non membre d'une association.

Un utilisateur peut cumuler plusieurs de ces groupes, mais ne peut pas également faire partie d'un groupe à privilèges élevés.

### Permissions

L'essentiel de l'application repose sur une logique de permissions dépendant de plusieurs types de contrôles :
- des fonctions utilitaires définies dans le fichier `plana/apps/users/models/user.py` dans la classe `User`.
- des permissions Django auto-générées, ou créées manuellement dans les fichiers des modèles concernés (fichiers `plana/apps/*/models/*.py`).
- du fait que l'utilisateur ait été crée en tant que gestionnaire via la commande `createmanageruser`.

Les permissions sont à affecter uniquement à des groupes d'utilisateurs et non individuellement (la table `users_user_user_permissions` n'est pas utilisée).

## Réinitialiser les permissions des groupes et les remplacer par celles par défaut

Le développement de l'application peut régulièrement amener à créer de nouvelles permissions ou à modifier leurs affectations aux groupes, amenant à son tour à devoir modifier les données injectées par les fixtures et les dizaines d'identifiants en découlant.

Une procédure a été mise en place pour simplifier la régénération de ces fixtures en particulier (après une possible migration de la base de données), évitant ainsi d'en modifier manuellement les identifiants :
1. Modifier les liens initiaux entre groupes et permissions définis dans le fichier `plana/settings/permissions.py` pour ajouter/modifier/retirer les liens concernés.
2. Exécuter la commande `python manage.py reset_permissions` pour supprimer tous les anciens liens entre permissions et groupes, les remplacer par les nouveaux en base de données, et régénérer les fichiers de fixtures concernés (l'argument `--flush` est également disponible pour vider la base de données et remettre les identifiants à zéro au préalable).
