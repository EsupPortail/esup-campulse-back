---
title: Base de données
weight: 105
---

## Docker

La configuration Docker fournit :
- une base de données PostgreSQL sur le port `5432` (attention à ne pas entrer en conflit avec une instance de PostgreSQL active, changer le port ou la désactiver avec `$ sudo service postgresql stop` au besoin).
- un serveur de mails de test sur le port `1080` via [MailDev](https://maildev.github.io/maildev/).

La configuration paramétrable via le fichier `docker-compose.yml` situé à la racine du projet et peut être lancée via `$ sudo docker compose up -d` ou arrêtée via `$ sudo docker compose down`.

La variable de configuration `DATABASES` est utilisée pour stocker les identifiants de la base de données sur certains environnements.

## Activation des extensions

L'extension PostgreSQL `unaccent` est nécessaire pour gérer les caractères accentués pour les fonctionnalités de recherche de contenu.
- Se connecter à la base de données via `$ psql -U NOM_UTILISATEUR -h localhost`.
- Activer l'extension avec `# CREATE EXTENSION unaccent;`.

## Import initial des données

Après avoir activé l'environnement virtuel :
- Exécuter `$ python manage.py migrate` pour initialiser la structure de la base de données.
- Exécuter `$ python manage.py initial_import` pour ajouter le jeu de données initial minimal au bon fonctionnement de l'application.

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
