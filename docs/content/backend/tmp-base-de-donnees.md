---
title: (WIP) Base de données
weight: 999
---

## Ajout d'extensions PostgreSQL

Pour faire fonctionner correctement l'application Plan A, certaines extensions de base de données Postgresql sont nécessaires :
- `unaccent` (gestion des caractères accentués pour le formulaire de recherche d'association)

On peut les ajouter à la base de données locale avec les commandes suivantes : 

```
$ psql -U plana -h localhost
```
Va permettre de se connecter à la base de données locale en tant qu'utilisateur plana.

```
plana=# CREATE EXTENSION unaccent;
```
Va permettre d'ajouter l'extension `unaccent` à la base de données une fois connecté en tant que plana.

## Comptes de tests mis à disposition

Afin de pouvoir tester l'application dans des conditions optimales, plusieurs comptes de tests sont présents en base de données une fois les fixtures par défaut chargées (cf. [Fixtures de l'application](/Gestion de la base de données/Fixtures de l'application)).

Ce sont tous des comptes locaux (pas d'identification via CAS), et disposent tous d'un mot de passe commun (excepté pour `compte-non-valide@mail.tld` qui est un compte de test inactif).

Le mot de passe est le suivant : `motdepasse`

Voici la liste de tous ces comptes avec leurs identifiants : 

1. `admin@admin.admin` (permet d'accéder à l'interface d'administration de l'application : `http://localhost:8000/admin/`)
2. `compte-non-valide@mail.tld` (nouveau compte avec adresse email non validée)
3. `gestionnaire-svu@mail.tld`
4. `gestionnaire-uha@mail.tld`
5. `gestionnaire-crous@mail.tld`
6. `membre-fsdie-idex@mail.tld`
7. `membre-culture-actions@mail.tld`
8. `membre-commissions@mail.tld`
9. `etudiant-porteur@mail.tld`
10. `etudiant-asso-hors-site@mail.tld`
11. `etudiant-asso-site@mail.tld`
12. `president-asso-hors-site@mail.tld`
13. `president-asso-site@mail.tld`
14. `president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld`
15. `compte-presque-valide@mail.tld` (nouveau compte avec adresse email validée)

## Fixtures de l'application

Pour charger les jeux de données de base l'application il suffit de lancer les deux commandes suivantes à la racine du projet :

```
$ python manage.py loaddata plana/apps/*/fixtures/*.json
$ python manage.py loaddata plana/libs/*/fixtures/*.json
```

La première permet de remplir la base de données avec un jeu de données de test pour l'application (comptes, associations, etc)

La seconde est dédiée aux templates de mails utilisés par défaut au sein de l'application.

## Migrer les modèles de données

Afin de mettre à jour les différents modèles de données dans la base de données on utilise les commandes suivantes à la racine du projet : 

```
$ python manage.py makemigrations
```
Pour mettre à jour les fichiers de migrations de l'application à partir des changements effectués sur les modèles de données (fichiers `models.py` ou fichiers présents dans les répertoires `models` de chaque sous-application de Plan A, devant être commités par la suite pour éviter tout conflit).

```
$ python manage.py migrate
```
Pour migrer les fichiers de migrations générés précédemment dans la base de données et ainsi mettre à jour le modèle de données. 

Une fois cette action effectuée, il est possible que certaines fixtures doivent être modifiées pour correspondre à ces nouveaux modèles de données selon les modifications qui leur ont été apportées.

## Réinitialiser la base de données

Il peut parfois être nécessaire de vider entièrement la base de données afin d'éviter de trop lourds conflits lors d'un dump ou une migration de la BDD.

Il est possible d'utiliser la commande suivante : 
```
$ python manage.py flush
```
