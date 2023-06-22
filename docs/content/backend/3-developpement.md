---
title: Développement
weight: 23
pre: "<b>3. </b>"
---

## Commandes

Voici une liste non-exhaustive de commandes pratiques utilisées pour le développement de l'application.

Les commandes suivantes s'éxecutent à la racine du projet, avec le virtualenv activé : 

### Lancer le serveur local

```
$ python manage.py runserver
```

### Régénérer la structure et le contenu de la base de données

```
$ python manage.py clean_database
```

### Vider le contenu du bucket S3 de l'environnement courant

```
$ python manage.py clean_storages
```

### Régénérer le fichier de traductions

```
$ python manage.py makemessages -l fr --extension html,txt,py
```
(Penser également à revérifier les traductions générées dans les fichiers présents dans le dossier `plana/locale`.)

### Réordonner les imports

```
$ isort plana
```

### Linter les fichiers

```
$ black plana
```

### Détecter les autres erreurs non lintables des fichiers

Génère un fichier `pylint.json` à la racine du projet, contenant la liste des erreurs.

```
$ pylint plana --output-format=json:pylint.json
```

(Ajouter `export PYTHONPATH=$PYTHONPATH:DOSSIER_DU_PROJET` au fichier `postactivate` de l'environnement virtuel au besoin.)

### Mettre à jour automatiquement le fichier de documentation de l'API

```
$ python manage.py spectacular --file schema.yml
```

## Routes de base

Voici une liste non-exhaustive des routes de base utilisées lors du développement de l'application :

### URL principale du frontend

http://localhost:3000/

### URL principale du backend

http://localhost:8000/

### URLs backend de documentation de l'api

- http://localhost:8000/api/schema/  
Permet de télécharger un fichier YAML contenant la documentation.

- http://localhost:8000/api/schema/swagger-ui/  
Permet de consulter la documentation de l'API en mode Swagger.
 
- http://localhost:8000/api/schema/redoc/  
Permet de consulter la documentation de l'API en mode Redoc.

### URL du serveur mail

http://localhost:1080/

## Tests unitaires

L'application Plan A dispose de nombreux tests unitaires exécutables localement.

On peut les exécuter via la commande suivante à la racine du projet avec l'environnement virtuel activé et le Docker local lancé, avec l'une des deux commandes suivantes :

```
$ tox
$ DEFAULT_DB_TEST_HOST=localhost tox
```

Tester des fichiers individuellement est également possible :

```
$ DEFAULT_DB_TEST_HOST=localhost coverage run manage.py test plana -v 2 --settings=plana.settings.unittest -p "NOM_DU_FICHIER.py"
```

---

Commande pour voir de façon graphique le coverage des tests unitaires : 

```
$ firefox htmlcov/index.html
```
