# PlanA / Opaline

## Health

### develop

[![pipeline status](https://git.unistra.fr/di/plan_a/plana/badges/develop/pipeline.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)
[![coverage report](https://git.unistra.fr/di/plan_a/plana/badges/develop/coverage.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)

## Description

Création d'une application web pour la gestion des associations étudiantes et de leurs projets.

## Prérequis

python (>=3.9), pip, virtualenv, virtualenvwrapper

## Installation rapide en ligne de commande

1. Créer l'environnement virtuel : `mkvirtualenv plana`.
2. Configurer les variables d'environnement nécessaires (fichier `postactivate` du venv) : `export DJANGO_SETTINGS_MODULE=plana.settings.dev`.
3. Ajouter l'extension unaccent à PostgreSQL : se connecter à l'interface en ligne de commande psql (`psql -U plana -h localhost`) puis `CREATE EXTENSION unaccent;` puis `\q` pour quitter.
4. Lancer la base de données PostgreSQL et le service de mail en local avec Docker : `sudo docker-compose up -d` ou `sudo docker compose up -d`.
5. Lancer l'environnement virtuel : `workon plana`.
6. Installer les dépendances sans Poetry : `pip install -r requirements/dev.txt`.
7. Migrer les modèles de données dans la base de données : `python manage.py migrate`.
8. Charger les fixtures dans la base de données : `python manage.py loaddata plana/apps/*/fixtures/*.json` et `python manage.py loaddata plana/libs/*/fixtures/*.json`.
9. Lancer le serveur local : `python manage.py runserver`.

## Liens

- [http://localhost:3000/](http://localhost:3000/) : frontend.
- [http://localhost:8000/](http://localhost:8000/) : backend.
- [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/) : télécharger un fichier YAML contenant la documentation.
- [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/) : consulter la documentation de l'API en mode Swagger.
- [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/) : consulter la documentation de l'API en mode Redoc.
- [http://localhost:1080/](http://localhost:1080/) : serveur mail.

## Développement

Consulter [le wiki d'aide au développement](https://git.unistra.fr/di/plan_a/plana/-/wikis/home) pour obtenir des instructions détaillées sur chaque commande.

### Avant un commit

- Mettre à jour les dépendances : `poetry lock && poetry install --sync && ./generate_requirements.sh`.
- Régénérer le fichier de traductions : `python manage.py makemessages -l fr --extension html,txt,py`.
- Régénérer le fichier de documentation de l'API : `python manage.py spectacular --file schema.yml`.
- Réordonner les imports et linter les fichiers : `isort plana && black plana`.
- Exécuter les tests unitaires : `tox` ou `DEFAULT_DB_TEST_HOST=localhost tox`.

### Autres commandes

- Réinitialiser la structure de la base de données et son contenu : `python manage.py clean_database`.
- Créer un utilisateur gestionnaire : `python manage.py createmanageruser --email EMAIL --firstname FIRST_NAME --lastname LAST_NAME --group GROUP_NAME [--institution INSTITUTION] [--password PASSWORD]`.
- Réinitialiser les permissions et leurs fixtures : `python manage.py reset_permissions`.
- Obtenir une liste des améliorations de code possibles (génère un fichier `pylint.json` à la racine) : `pylint plana --output-format=json:pylint.json`.
- Visualiser le coverage des tests unitaires : `firefox htmlcov/index.html`.

### Déployer sur le serveur de test

- Déployer le projet : `fab tag:develop test deploy -u root`.
- Charger les fixtures générales : `fab test custom_manage_cmd:loaddata\ plana/apps/*/fixtures/*.json -u root`.
- Charger les fixtures des templates de mails : `fab test custom_manage_cmd:loaddata\ plana/libs/*/fixtures/*.json -u root`.

Le front est accessible à cette adresse : [https://plana-test.app.unistra.fr/](https://plana-test.app.unistra.fr/)

Le back est accessible à cette adresse : [https://plana-api-test.app.unistra.fr/](https://plana-api-test.app.unistra.fr/)

### Déployer sur le serveur de prod

- Déployer le projet : `fab tag:release/X.X.X prod deploy -u root`.
- Charger les fixtures obligatoires : `fab prod custom_manage_cmd:initial_import -u root`.
