---
title: Commandes
weight: 116
---

## Commandes générales de développement

- `$ python manage.py runserver` : lancer le serveur de développement.
- `$ python manage.py makemigrations` : créer de nouvelles migrations de l'application après modification de la structure de la BDD dans les fichiers des dossiers `models` (puis exécuter `$ python manage.py migrate` ensuite).
- `$ python manage.py makemessages -l fr --extension html,txt,py` : régénérer les fichiers de traductions du dossier `plana/locale`.
- `$ python manage.py spectacular --file schema.yml` : régénérer le fichier OpenAPI `schema.yml`.
- `$ python manage.py clean_storages` : réinitialiser le contenu du bucket S3 de l'environnement courant.
- `$ python manage.py reset_permissions [--flush]` : régénère les fixtures de permissions du dossier `plana/apps/groups/fixtures` d'après le fichier `plana/settings/permissions.py` (avec une option `--flush` pour réinitialiser les identifiants).

## Régénérer la base de données

- `$ python manage.py flush` : vider le contenu de la base de données.
- `$ python manage.py migrate` : mettre à jour la structure de la base de données (à précéder de `$ python manage.py makemigrations` pour créer les fichiers de migrations au besoin).
- `$ python manage.py loaddata plana/apps/*/fixtures/*.json` : ajouter les jeux de données de test (utilisateurs, associations, projets, ...).
- `$ python manage.py loaddata plana/libs/*/fixtures/*.json` : ajouter les jeux de données liées aux templates de mails.
- `$ python manage.py clean_database` : équivalent des commandes `flush`, `migrate`, `loaddata` en une seule commande.

## Mise à jour des dépendances avec Poetry

- `$ poetry lock` : mise à jour de la liste des dépendances en cache.
- `$ poetry install --sync` : installation des dépendances.
- `$ ./generate_requirements.sh` : régénération des fichiers du dossier `requirements` avec les dépendances mises à jour.

## Tests unitaires

- `$ tox` ou `$ DEFAULT_DB_TEST_HOST=localhost tox` : lancer les tests unitaires (le fichier `htmlcov/index.html` permet de consulter le coverage).

## Autres commandes

- `$ isort plana` : trier les imports.
- `$ black plana` : linter les fichiers.
- `$ pylint plana --output-format=json:pylint.json` : liste des erreurs non lintables exportées dans un fichier `pylint.json`.
- `$ cd docs && hugo server && cd ..` : lancer le serveur de développement de la documentation.