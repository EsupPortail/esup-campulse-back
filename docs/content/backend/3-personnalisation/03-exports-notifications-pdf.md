---
title: Exports et notifications PDF
weight: 123
---

Les fichiers utilisés pour la génération de PDF sont externalisés dans un dépôt distinct du projet PlanA. Ils sont hébergés dans la section du bucket S3 au nom défini par la variable de configuration `S3_PDF_FILEPATH`.

Au sein de cette section, l'arborescence suivante est suggérée :
- `css` : feuilles de styles statiques appliquées aux templates
- `fonts` : polices d'écriture statiques utilisées
- `img` : images statiques (logos affichés)
- `templates/exports` : templates HTML d'exports (récap de projet, récap de charte, ...).
- `templates/notifications` : templates HTML de notifications attachées aux emails (attribution ou refus d'une aide, ...).

Les variables de configuration `TEMPLATES_PDF_EXPORTS_FOLDER` et `TEMPLATES_PDF_NOTIFICATIONS_FOLDER` permettent de modifier les chemins des deux derniers dossiers au besoin.

## Notifications d'attribution / de refus envoyées par email

Les notifications de subventions sont des fichiers PDF présents en pièces jointes des mails informant les utilisateurs d'un succès, d'un refus, ou d'un report d'une demande de subventionnement.

### Types de notifications

Ces notifications sont reliées intrinsèquement aux différents organismes de fonds qui vont traiter les demandes de subventionnement.

Nous avons ainsi 4 types de notifications, aux codes formatés comme suit :
- `NOTIFICATION_{FUND_ACRONYM}_DECISION_ATTRIBUTION` : Document présentant l'aspect légal de l'attribution de la subvention par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_ATTRIBUTION` : Document visant à prévenir les concernés que leur demande de subventionnement a été acceptée par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_REJECTION` : Document informant les concernés que leur demande de subventionnement a été refusée par le fonds désigné.
- `NOTIFICATION_{FUND_ACRONYM}_PROJECT_POSTPONED` : Document informant les concernés que leur demande de subventionnement a été reportée à une commission future pour leur projet par le fonds désigné.

L'attribut `{FUND_ACRONYM}` ci-dessus doit obligatoirement être remplacé par l'acronyme en base de données du fonds concerné en majuscules.

Ce code est ensuite stocké dans la table `contents_content`, avec les textes des contenus qui constituent le corps du PDF de notification renvoyé.

### Variables présentes dans les contenus

Différentes variables par défaut sont présentes dans les différents contenus renvoyés et sont alors utilisables dans les différents templates de contenus.

Communes à tous les contenus : 
- `project_name` : Le nom du projet. (string)
- `date` : La date du jour à laquelle le document est généré. (date)
- `date_commission` : Date de la commission dans laquelle le projet est soumis pour le fonds désigné. (date)
- `content` : Objet Content contenant toutes les informations nécessaires au rendu du PDF de notification, il s'utilise de la manière suivante dans les templates : `{{ content.header }}` par exemple.
- `owner` : Dictionnaire contenant les informations essentielles du dépositaire du projet, c'est à dire son nom et son adresse (de l'association ou du porteur individuel de projet). Il s'utilise de la manière suivante dans les templates : `{{ owner.name }}` ou `{{ owner.address }}` selon l'information voulue.

Variables spécifiques à certains contenus uniquement : 
- `amount_earned` : Uniquement pour les notifications d'attribution, montant alloué au projet par le fonds désigné. (int)
- `comment` : Uniquement pour les notifications de refus et de report, dernier commentaire laissé sur le projet, sensé indiquer pourquoi un report ou un refus a été décidé. (string)

### Format des contenus

Les contenus sont par défaut sous format texte, cependant il est recommandé d'y ajouter des balises HTML inline (comme des `<h1>`, des `<p>` etc). A contrario, il n'est pas recommandé d'utiliser des balises block (comme des `<div>`) et de privilégier leur utilisation directement dans le template HTML au besoin.

Pour utiliser les variables ci-dessus, il suffit de les intégrer au texte de contenu sous le format `{{ var_name }}`. Elles seront alors reconnues et interprétées par le système de templating Django.

Pour chaque type de notification il n'y a qu'un seul objet Content lié, composé lui-même d'un `header`, d'un `body`, d'un `footer`, et d'un `aside` qui peuvent être utilisés pour ajouter du contenu supplémentaire au document.

Pour que l'export PDF des notifications se fasse correctement, il faut obligatoirement importer les données de Content avec la syntaxe `{% resolve %}{{ content.body|safe }}{% endresolve %}` afin de traduire le contenu du texte en HTML et d'interpréter les variables qui y sont situées.
