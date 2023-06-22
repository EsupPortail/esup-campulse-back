---
title: Configuration
weight: 22
pre: "<b>2. </b>"
---

## Configuration Django

Dans les fichiers de settings de l'application, il y a de nombreuses variables personnalisées qui permettent de plus ou moins configurer certains comportements de l'application.

### Authentification

#### URL du serveur CAS

```
CAS_SERVER = "https://cas.domain.tld/cas/"
```

#### URLs CAS autorisées / permettant de valider les tickets

```
CAS_AUTHORIZED_SERVICES = [
    "https://plana-front.domain.tld/cas-login",
    "https://plana-front.domain.tld/cas-register",
]
```

### Liens générés dans les templates de mails

#### Lien de base vers le front dans les emails

```
EMAIL_TEMPLATE_FRONTEND_URL = "https://plana-front.domain.tld/"
```

#### Lien vers la page d'adresse mail vérifée dans les mails

```
EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_URL = (
    EMAIL_TEMPLATE_FRONTEND_URL + "register-verify-email/"
)
```

#### Lien vers la page de réinitialisation de mot de passe dans les mails

```
EMAIL_TEMPLATE_PASSWORD_RESET_URL = (
    EMAIL_TEMPLATE_FRONTEND_URL + "password-reset-confirm/"
)
```

#### Lien vers la page de modification de mot de passe dans les mails

```
EMAIL_TEMPLATE_PASSWORD_CHANGE_URL = (
    EMAIL_TEMPLATE_FRONTEND_URL + "dashboard/password-change-url/"
)
```

#### Lien vers la page de validation des utilisateurs côté gestionnaire dans les mails

```
EMAIL_TEMPLATE_ACCOUNT_VALIDATE_URL = (
    EMAIL_TEMPLATE_FRONTEND_URL + "dashboard/validate-users/"
)
```

#### Lien de documentation présent dans les mails

```
APP_DOCUMENTATION_URL = "https://documentation.domain.tld/"
```

### Stockage AWS (images et documents)

#### ID de clé d'accès

```
AWS_ACCESS_KEY_ID = '{{ s3_access_key }}'
```

#### Clé d'accès secrète

```
AWS_SECRET_ACCESS_KEY = '{{ s3_secret_key }}'
```

#### Nom du bucket de stockage

```
AWS_STORAGE_BUCKET_NAME = '{{ s3_bucket }}'
```

#### URL du stockage S3

```
AWS_S3_ENDPOINT_URL = '{{ s3_endpoint }}'
```

### Comportements particuliers

#### Valeur par défaut définissant si une association est site ou hors site

```
ASSOCIATION_IS_SITE_DEFAULT = False

```
Ce paramètre correspond à une spécificité de l'Université de Strasbourg, il doit être passé à `True` si l'application ne comporte pas cette spécificité.

#### Domaines d'adresses mail non-autorisés à créer des comptes locaux

```
RESTRICTED_DOMAINS = ["unistra.fr", "etu.unistra.fr"]
```

Dans notre cas les domaines présents ici correspondent à des adresses pouvant se connecter à CAS.

## Lancer la BDD et le serveur de mail avec Docker

Pour le développement, il existe un fichier `docker-compose.yml` à la racine du projet qui permet de paramétrer la base de données locale et le serveur de mail local.  
Il devient alors possible de disposer d'une base de données de tests ainsi que d'un serveur de mail local en ayant juste une commande à lancer à la racine du projet.

[Docker](https://docs.docker.com/) est un prérequis pour pouvoir lancer la commande.

Aucune instance de Postgresql ne doit être active sur la machine pour pouvoir lancer son conteneur (des erreurs de ports peuvent survenir).

La commande à entrer pour démarrer le service diffère en fonction de la version et/ou de la configuration de Docker.

### Commande pour lancer la base de données et le serveur de mail avec docker

```
$ sudo docker-compose up -d
$ sudo docker compose up -d
```

### Commande pour stopper le service

```
$ sudo docker-compose down
$ sudo docker compose down
```

### Importer un jeu de données initial

```
$ python manage.py initial_import
```

## Configuration et fonctionnement des templates de mails

Les templates de mails du projet sont gérés par un module externe situé dans le dossier `plana/libs/mail_template`.

Des templates de base sont proposés dans le dossier `fixtures` inclus.

Localement, les emails sont envoyés et reçus via [MailDev](https://maildev.github.io/maildev/), lancé via le conteneur Docker (voir [Lancer la BDD et le serveur de mail avec Docker](https://git.unistra.fr/di/plan_a/plana/-/wikis/Aides%20pour%20le%20d%C3%A9veloppement/Lancer%20la%20BDD%20et%20le%20serveur%20de%20mail%20avec%20Docker)).

La plupart des mails sont reçus ou envoyés par l'adresse spécifiée dans la variable `DEFAULT_FROM_EMAIL` définie dans les paramètres du projet. D'autres seront reçus ou envoyés par l'adresse spécifiée dans le compte utilisateur ou dans l'institution.

## Génération des clés JWT et AGE

Deux paires de clés de chiffrement doivent être générées dans le dossier `keys` à la racine du projet.

### Clés JWT

L'authentification utilise des tokens JWT SHA256. La commande `python manage.py generate_jwt_keys` permet de générer les fichiers contenant les clés publique et privée.

### Clés AGE

Les fichiers mis en ligne par les étudiants peuvent contenir des informations confidentielles. La classe `DocumentUpload` les gérant stocke donc les fichiers de manière chiffrée.

Générer les clés de chiffrement se fait à l'aide du package [age](https://github.com/FiloSottile/age) qu'il est nécessaire d'installer. Puis la commande `python manage.py generate_age_keys` permet de générer les fichiers contenant les clés publique et privée.

Attention, le package `age` n'est pas supporté par certaines anciennes versions de GNU/Linux. La commande `python manage.py generate_age_keys` ne pourra donc être exécutée. Dans ce cas, il est nécessaire de générer de nouvelles clés localement et de les déplacer manuellement sur le serveur :

```
$ python manage.py generate_age_keys
$ scp -r keys/age-private-key.key USER@DOMAIN.TLD:/APP_FOLDER/keys/
$ scp -r keys/age-public-key.key USER@DOMAIN.TLD:/APP_FOLDER/keys/
```

## Tâches CRON

Certains processus de l'application dépendent de différentes tâches CRON pour se mettre à jour correctement (expiration de documents, comptes inactifs, politique de mots de passe, etc...).

Les différentes commandes exécutables via des tâches CRON se trouvent dans le répertoire `plana/management/commands` du dépôt, avec les commandes personnalisées d'aide au développement :
- `account_expiration` (suppression des comptes après un an d'inactivité).
- `association_expiration` (changement de statut de la charte des associations qui vient à expirer ou expire).
- `commission_expiration` (suppression des liens entre brouillons de projets et dates de commissions expirées).
- `document_expiration` (changement de statut des documents (chartes de subventionnement) qui viennent à expirer ou expirent).
- `goa_expiration` (liste des associations dont la date de dernière Assemblée Générale Ordinaire a plus de 11 mois).
- `password_expiration` (réinitialisation des mots de passe après un an sans changement).
- `project_expiration` (suppression des projets vieux de dix ans).
- `review_expiration` (rappel de soumettre le bilan d'un projet subventionné).
