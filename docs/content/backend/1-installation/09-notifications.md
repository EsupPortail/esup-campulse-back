---
title: Notifications de subvention
weight: 109
---

Les notifications de subventions sont des fichiers pdf présents en pièces jointes des mails informant les utilisateurs d'un succès, d'un refus, ou d'un report d'une demande de subventionnement.

## Types de notifications

Ces notifications sont reliées intrinsèquement aux différents organismes de fonds qui vont traiter les demandes de subventionnement.

Nous avons ainsi 4 types de notifications, formattés comme suit :
- `NOTIFICATION_{FUND_ACRONYM}_DECISION_ATTRIBUTION` : Document présentant l'aspect légal de l'attribution de la subvention par le fonds désigné.
- `NOTIIFICATION_{FUND_ACRONYM}_ATTRIBUTION` : Document visant à prévenir les concernés que leur demande de subventionnement a été acceptée par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_REJECTION` : Document informant les concernés que leur demande de subventionnement a été refusée par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_PROJECT_POSTPONED` : Document informant les concernés que leur demande de subventionnement a été reportée à une commission future pour leur projet par le fonds désigné.

Ces différents types de notifications sont configurables dans le fichier `settings/base.py` du projet afin d'en personnaliser les intitulés en fonction des différents fonds gérés par l'application.
L'attribut `{FUND_ACRONYM}` ci-dessus doit obligatoirement être remplacé par l'acronyme en base de données du fonds concerné en majuscules.

## Lien entres les types de notifications et les templates PDF

Aperçu du fichier `settings/base.py` : 
```python
TEMPLATES_NOTIFICATIONS = {
    "NOTIFICATION_EXAMPLE_DECISION_ATTRIBUTION": "./notifications/example/decision_attribution.html",
    "NOTIFICATION_TEST_DECISION_ATTRIBUTION": "./notifications/test/example.html",

    "NOTIFICATION_EXAMPLE_ATTRIBUTION": "./notifications/example/attribution.html",
    "NOTIFICATION_TEST_ATTRIBUTION": "./notifications/test/example.html",

    "NOTIFICATION_EXAMPLE_REJECTION": "./notifications/example/rejection.html",
    "NOTIFICATION_TEST_REJECTION": "./notifications/test/example.html",

    "NOTIFICATION_EXAMPLE_PROJECT_POSTPONED": "./notifications/example/postpone.html",
    "NOTIFICATION_TEST_PROJECT_POSTPONED": "./notifications/test/example.html",
}
```
C'est à cet endroit que les noms de notifications sont reliés aux templates HTML présents dans le répertoire `templates` du projet. Ces templates servent au formattage des données sur le document final, et permettent une personnalisation totale avec du CSS et quelques variables par défaut.

## Spécificités des templates PDF

Les templates PDF sont ceux utilisés par Django, ils utilisent donc jinja2 et des templatetags.
Pour que l'export PDF des notifications se fasse correctement, il faut obligatoirement importer les données comme dans le modèle d'exemple mis à disposition : `templates/notifications/example/example.html`. C'est à dire en important les données avec la syntaxe `{% resolve %}{{ content.body|safe }}{% endresolve %}` afin de traduire le contenu du texte en HTML et d'interpréter les variables qui y sont situées.

## Stockage des textes de contenus

Les textes des contenus qui constituent le corps du PDF de notification renvoyé sont stockés en base de données dans la table `content`.

Ils doivent être renseignés avec l'attribut `code` similaire au code de notification présent dans le fichier de settings expliqué plus haut.

Les contenus peuvent être vides mais ils doivent au moins être créés en base de données en amont avec le bon code.

## Variables présentes dans les contenus

Différentes variables par défaut sont présentes dans les différents contenus renvoyés et sont alors utilisables dans les différents templates de contenus.

Communes à tous les contenus : 
- `project_name` : Le nom du projet. (string)
- `date` : La date du jour à laquelle le document est généré. (date)
- `date_commission` : Date de la commission dans laquelle le projet est soumis pour le fonds désigné. (date)
- `content` : Objet Content contenant toutes les informations nécessaires au rendu du PDF de notification, il s'utilise de la manière suivante dans les templates : `{{ content.header }}` par exemple.
- `owner` : Dictionnaire contenant les informations essentielles du dépositaire du projet, c'est à dire son nom et son adresse (de l'association ou du porteur individuel de projet). Il s'utilise de la manière suivante dans les templates : `{{ owner.name }}` ou `{{ owner.address }}` selon l'information voulue.

Variables spécifiques à certains contenus uniquement : 
- `amount_earned` : Uniquement pour les notifications d'attribution, montant alloué au projet par le fonds désigné. (int)
- `amount_earned_litteral` : Uniquement pour les notifications d'attribution, montant alloué au projet par le fonds désigné, en toutes lettres (langue définie selon la locale système). (string)
- `comment` : Uniquement pour les notifications de refus et de report, dernier commentaire laissé sur le projet, sensé indiquer pourquoi un report ou un refus a été décidé. (string)

## Format des contenus

Les contenus sont par défaut sous format texte, cependant il est recommandé d'y ajouter des balises HTML inline (comme des `<h1>`, des `<p>` etc). A contrario, il n'est pas recommandé d'utiliser des balises block (comme des `<div>`) et de privilégier leur utilisation directement dans le template HTML au besoin.

Pour utiliser les varriables ci-dessus, il suffit de les intégrer au texte de contenu sous le format `{{ var_name }}`. Elles seront alors reconnues et interprétées par le système de templating Django.

Pour chaque type de notification il n'y a qu'un seul objet Content lié, composé lui-même d'un `header`, d'un `body`, d'un `footer`, et d'un `aside` qui peuvent être utilisés pour ajouter du contenu supplémentaire au document.
