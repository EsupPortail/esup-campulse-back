---
title: Installation
weight: 21
pre: "<b>1. </b>"
---

## Créer l'environnement virtuel

Commande pour créer l'environnement vituel avec `virtualenvwrapper` (cf. [Documentation de virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)) : 

```
$ mkvirtualenv plana
```
Python doit être en version `3.9`.

---

Commande pour lancer l'environnement virtuel (toujours avec virtualenvwrapper) : 

```
$ workon plana
```

## Variables d'environnement nécessaires

Pour que l'application tourne correctement, différentes variables d'environnement sont nécessaires.

Elles se trouvent au niveau du fichier `bin/postactivate` de l'environnement virtuel dédié à l'application.

### Définir le fichier de configuration (environnement) utilisé par l'application

```
export DJANGO_SETTINGS_MODULE=plana.settings.dev
```

### Upload d'images et de documents sur le stockage S3

```
export AWS_ACCESS_KEY_ID=AccESSkeyId
export AWS_SECRET_ACCESS_KEY=secREtaCCEsskeY
export AWS_STORAGE_BUCKET_NAME=bucket_name
export AWS_S3_ENDPOINT_URL=https://s3.domain.example
```

### Communication avec le serveur LDAP pour l'ajout de comptes distants via l'interface de gestion

```
export ACCOUNTS_API_SPORE_DESCRIPTION_FILE="https://rest-api-domain.tld/path/description.json"
export ACCOUNTS_API_SPORE_BASE_URL="https://ldapws-domain.tld"
export ACCOUNTS_API_SPORE_TOKEN="t0k3n"
```

## Installation des dépendances

Pour fonctionner, l'application Plan A dépend de nombreuses librairies listées dans les fichiers du répertoire [`requirements`](https://git.unistra.fr/di/plan_a/plana/-/tree/develop/requirements) ou dans le fichier [`pyproject.toml`](https://git.unistra.fr/di/plan_a/plana/-/blob/develop/pyproject.toml), tous deux présents à la racine du projet.   
Il faut installer ces dépendances dans le virtualenv dédié à l'application.  

On peut installer ces dépendances via deux méthodes : avec ou sans l'aide de Poetry.

### Installer les dépendances dans le virtualenv sans Poetry

Avec le virtualenv activé, lancer la commande suivante :

```
$ pip install -r requirements/dev.txt
```
---

### Installer les dépendances dans le virtualenv avec Poetry

Avec le virtualenv activé, lancer la commande suivante :

```
$ poetry install --sync
```

---

### Mettre à jour les dépendances avec Poetry

Avec le virtualenv activé, lancer les commandes suivantes :

```
$ poetry lock
$ poetry install --sync
$ ./generate_requirements.sh
```
