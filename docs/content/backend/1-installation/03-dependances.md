---
title: Dépendances logicielles
weight: 103
---

L'application dépend de nombreuses librairies installables via deux méthodes différentes.

## Installation manuelle

Les dépendances sont listées dans le répertoire `requirements`.
- Activer l'environnement virtuel.
- Exécuter la commande `pip install -r requirements/[ENVIRONNEMENT].txt` à la racine du projet.

## Installation avec Poetry

Les dépendances sont listées dans le fichier `pyproject.toml`.
- Activer l'environnement virtuel.
- Exécuter la commande `poetry install [[--without dev]] --sync` à la racine du projet.

## Documentation

La documentation est gérée avec [Hugo](https://gohugo.io/installation/).
- Installer son package est requis pour la modifier.
- Exécuter `git submodule update --init --recursive` pour installer le thème.
- Exécuter `hugo server` pour lancer le serveur de développement de la documentation.
