---
title: Base de données
weight: 105
---

## Activation des extensions

L'extension PostgreSQL `unaccent` est nécessaire pour gérer les caractères accentués pour les fonctionnalités de recherche de contenu.
- Se connecter à la base de données via `$ psql -U NOM_UTILISATEUR -h localhost`.
- Activer l'extension avec `# CREATE EXTENSION unaccent;`.

## Import initial des données

Après avoir activé l'environnement virtuel :
- Exécuter `$ python manage.py migrate` pour initialiser la structure de la base de données.
- Exécuter `$ python manage.py initial_import [--test]` pour ajouter le jeu de données initial minimal au bon fonctionnement de l'application (spécifier l'option `--test` pour ajouter des données de test pour le développement).

## Création de comptes à privilèges élevés

Des comptes avec des droits élevés peuvent être crées via la commande suivante :  
```sh
$ python manage.py createmanageruser \
  --email EMAIL \
  --firstname FIRST_NAME \
  --lastname LAST_NAME \
  --group GROUP_NAME \
  [--cas IDENTIFIANT_CAS] \
  [--institution INSTITUTION] \
  [--superuser]
``` 
Si `--institution` n'est pas spécifié, le gestionnaire créé aura des droits sur tous les établissements.  
Si `--superuser` est spécifié, le gestionnaire aura également accès à l'interface d'administration de Django.  
Le compte peut également être crée via l'interface d'administration de Django, mais il sera alors nécessaire de lui affecter des groupes et des établissements manuellement.
