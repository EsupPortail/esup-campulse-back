# PlanA

## Health

### Develop

[![pipeline status](https://git.unistra.fr/di/plan_a/plana/badges/develop/pipeline.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)
[![coverage report](https://git.unistra.fr/di/plan_a/plana/badges/develop/coverage.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)

## Description

Création d'une application web pour la gestion des associations étudiantes et de leurs projets.

## Prérequis

python (>=3.9), pip, virtualenv, virtualenvwrapper

## Installation

### Lancer la base de données PostgreSQL et le service de mail en local avec Docker

À la racine du projet :

```sh
$ sudo docker-compose up -d
```

Ou
```sh
$ sudo docker compose up -d
```

Pour stopper le service :
```sh
$ sudo docker-compose down
```

### Créer l'environnement virtuel

```sh
$ mkvirtualenv plana
```

### Configurer les variables d'environnement nécessaires (fichier postactivate du venv)

```sh
export DJANGO_SETTINGS_MODULE=plana.settings.dev
```

Les actions suivantes se font avec le virtualenv activé :

### Installer les dépendances de dev dans le virtualenv sans Poetry

```sh
$ pip install -r requirements/dev.txt
```

### Ajouter l'extension unaccent à PostgreSQL

```sh
$ psql -U plana -h localhost
plana=# CREATE EXTENSION unaccent;
```

### Migrer les modèles de données dans la base de données

```sh
$ python manage.py makemigrations
$ python manage.py migrate
```

### Charger les fixtures dans la base de données

```sh
$ python manage.py loaddata plana/apps/*/fixtures/*.json
$ python manage.py loaddata plana/libs/*/fixtures/*.json
```

Réinitialiser le contenu de la base de données au besoin :

```sh
$ python manage.py flush
```

### Lancer le serveur local

```sh
$ python manage.py runserver
```

## Développement

### Liens

- [http://localhost:3000/](http://localhost:3000/) : frontend.
- [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/) : télécharger un fichier YAML contenant la documentation.
- [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/) : consulter la documentation de l'API en mode Swagger.
- [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/) : consulter la documentation de l'API en mode Redoc.
- [http://localhost:1080/](http://localhost:1080/) : serveur mail.

### Comptes de test des fixtures

Mot de passe commun : `motdepasse`
- `gestionnaire-svu@mail.tld`
- `gestionnaire-crous@mail.tld`
- `membre-fsdie-idex@mail.tld`
- `membre-culture-actions@mail.tld`
- `membre-commissions@mail.tld`
- `etudiant-commissions@mail.tld`
- `etudiant-asso-hors-site@mail.tld`
- `etudiant-asso-site@mail.tld`
- `president-asso-hors-site@mail.tld`
- `president-asso-site@mail.tld`
- `president-asso-hors-site-etudiant-asso-site@mail.tld`
- `president-asso-site-etudiant-asso-hors-site@mail.tld`

### Détecter de nouvelles chaînes de caractères à traduire

```sh
$ python manage.py makemessages -l fr --extension html,txt,py

```

### Linter les fichiers

```sh
$ black plana
```

### Réordonner les imports

```sh
$ isort plana
```

### Détecter les autres erreurs non lintables des fichiers

```sh
$ pylint plana --output-format=json:pylint.json
```

(Ajouter `export PYTHONPATH=$PYTHONPATH:DOSSIER_DU_PROJET` au fichier `postactivate` de l'environnement virtuel.)

### Mettre à jour automatiquement le fichier de documentation de l'API

```sh
$ python manage.py spectacular --file schema.yml
```

### Exécuter les tests localement

```sh
$ DEFAULT_DB_TEST_HOST=localhost tox
```

### Voir de façon graphique le coverage des tests unitaires

```sh
$ firefox htmlcov/index.html
```

### Mettre à jour les dépendances du projet

```sh
$ poetry lock
$ poetry install --sync
$ ./generate_requirements.sh
```

### Déployer sur le serveur de test

```sh
$ fab tag:develop test deploy -u root
$ fab test custom_manage_cmd:loaddata\ plana/apps/*/fixtures/*.json -u root
```
