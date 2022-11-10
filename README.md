# PlanA

## Health

### Master

[![pipeline status](https://git.unistra.fr/di/plan_a/plana/badges/master/pipeline.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/master)
[![coverage report](https://git.unistra.fr/di/plan_a/plana/badges/master/coverage.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/master)

### Develop

[![pipeline status](https://git.unistra.fr/di/plan_a/plana/badges/develop/pipeline.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)
[![coverage report](https://git.unistra.fr/di/plan_a/plana/badges/develop/coverage.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)

## Description

Création d'une application web pour la gestion des associations étudiantes et de leurs projets.

## Prérequis

python (>=3.9), pip, virtualenv, virtualenvwrapper

## Installation

### Lancer la base de données PostgreSQL et le service de mail en local avec Docker

A la racine du projet :

```
$ sudo docker-compose up -d
```

Et pour stopper le service :
```
$ sudo docker-compose down
```

### Création de l'environnement virtuel

```
$ mkvirtualenv plana
```

### Configuration des variables d'environnement nécessaires (fichier postactivate du venv)

```
export DJANGO_SETTINGS_MODULE=plana.settings.dev
```


Les actions suivantes se font avec le virtualenv activé :


### Installation des dépendances de dev dans le virtualenv

```
$ pip install -r requirements/dev.txt
```

### Migrer les modèles de données dans la base de données

```
$ python manage.py makemigrations
$ python manage.py migrate
```

### Chargement des fixtures dans la base de données

```
$ python manage.py loaddata plana/apps/*/fixtures/*.json
```

## Lancement du serveur en local
```
$ python manage.py runserver
```

## Détecter de nouvelles chaînes de caractères à traduire
```
$ python manage.py makemessages -l fr --extension html,txt,py

```
