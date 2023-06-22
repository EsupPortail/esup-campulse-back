---
title: Base de données
weight: 105
---

## Docker

La configuration Docker fournit :
- une base de données PostgreSQL sur le port `5432` (attention à ne pas entrer en conflit avec une instance de PostgreSQL active)
- un serveur de mails de test sur le port `1080` via [MailDev](https://maildev.github.io/maildev/).

Elle est paramétrable via le fichier `docker-compose.yml` situé à la racine du projet et peut être lancée via `$ sudo docker compose up -d` ou arrêtée via `$ sudo docker compose down`.

## Import initial des données

Après avoir activé l'environnement virtuel :
- Exécuter `$ python manage.py migrate` pour initialiser la structure de la base de données.
- Exécuter `$ python manage.py initial_import` pour ajouter le jeu de données initial minimal au bon fonctionnement de l'application.
