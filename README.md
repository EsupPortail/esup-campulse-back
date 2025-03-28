# PlanA / Campulse

## Health

### develop

[![pipeline status](https://git.unistra.fr/di/plan_a/plana/badges/develop/pipeline.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)
[![coverage report](https://git.unistra.fr/di/plan_a/plana/badges/develop/coverage.svg)](https://git.unistra.fr/di/plan_a/plana/-/commits/develop)

## Description

Création d'une application web pour la gestion des associations étudiantes et de leurs projets.  
Documentation technique accessible à l'adresse [https://di.pages.unistra.fr/plan_a/plana](https://di.pages.unistra.fr/plan_a/plana)  
Dépôt du front accessible à l'adresse [https://github.com/EsupPortail/esup-campulse-front](https://github.com/EsupPortail/esup-campulse-front)

### Instances en ligne

- Université de Strasbourg & Crous de Strasbourg [https://etu-campulse.fr/](https://etu-campulse.fr/)
-
-
-
-

## Technologies requises

- [Python](https://www.python.org/) (version >= 3.9)
- [PostgreSQL](https://www.postgresql.org/) (version >= 12)
- [S3](https://aws.amazon.com/fr/s3/) (serveur de stockage des images et documents)

## Technologies conseillées

- [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) (gestion de l'environnement virtuel)
- [Poetry](https://python-poetry.org/) (gestionnaire de dépendances)
- [age](https://github.com/FiloSottile/age) (chiffrement des documents privés)

## Technologies de développement

- [MailDev](https://github.com/maildev/maildev) (serveur mail)
- [isort](https://github.com/pycqa/isort) (tri des imports)
- [Black](https://github.com/psf/black) (linter général)
- [Pylint](https://github.com/pylint-dev/pylint) (linter avancé)
- [tox](https://github.com/tox-dev/tox) (tests unitaires)
- [Hugo](https://github.com/gohugoio/hugo) (documentation)
