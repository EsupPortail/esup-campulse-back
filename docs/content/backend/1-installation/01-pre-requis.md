---
title: Pré-requis
weight: 101
---


## Technologies requises

- [Python](https://www.python.org/) (version >= 3.9)
- [PostgreSQL](https://www.postgresql.org/) (version >= 12)
- [S3](https://aws.amazon.com/fr/s3/) (serveur de stockage des images et documents)

## Technologies conseillées

- [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) (gestion de l'environnement virtuel)
- [Docker](https://www.docker.com/) (déploiement de l'application)
- [Poetry](https://python-poetry.org/) (gestionnaire de dépendances)
- [age](https://github.com/FiloSottile/age) (chiffrement des documents privés)

## Technologies de développement

- [isort](https://github.com/pycqa/isort) (tri des imports)
- [Black](https://github.com/psf/black) (linter général)
- [Pylint](https://github.com/pylint-dev/pylint) (linter avancé)
- [tox](https://github.com/tox-dev/tox) (tests unitaires)
- [Hugo](https://github.com/gohugoio/hugo) (documentation)

## Docker

- Seuls Docker et S3 sont requis, la plupart des autres étapes d'installation sont automatisées.
- Copier-coller les fichiers `docker/**/.env.dev.dist` vers de nouveaux fichiers `docker/**/.env.dev` et y placer les variables d'environnement requises (voir étape "Environnement virtuel" et "Base de données").
- La configuration automatise les étapes suivantes :
  - Installation de la base de données.
  - Installation des paquets système.
  - Installation des librairies Python.
  - Import de jeux de données de test en base de données et dans le bucket local du S3.
  - Génération des clés JWT et AGE.
  - Exécution du serveur.
- Exécuter `sudo docker compose up -d` pour démarrer le container et `sudo docker compose down` pour l'arrêter.
