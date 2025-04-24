---
title: Personnalisation
weight: 412
---

## Spécificités de l'arborescence

### Templates

Deux répertoires clés sont utilisés : `exports` et `notifications`.

Dans le répertoire `exports` sont stockés les 4 templates de PDF spécifiques au fonctionnement de l'application dans sa globalité.
Ces derniers sont notamment relatifs aux différents exports de données (projets, chartes), il convient donc de garder les nommages présents dans l'arborescence pré-générée.

Dans le répertoire `notifications` sont définis les différents templates utilisés lors des notifications de subventionnements aux divers projets portés au sein de l'application.
Ces différents templates doivent être répartis en fonction des différents fonds, par exemple : 
```txt
└── notifications
    ├── FEEX
    │  ├── attribution.html
    │  └── rejection.html
    └── FPEX
        ├── attribution.html
        ├── decision_attribution.html
        ├── postpone.html
        └── rejection.html
```
Où FEEX et FPEX représentent les **acronymes** des fonds définis au sein de l'application.
Chaque fonds peut disposer de 4 templates correspondants aux différentes actions : 
- attribution (`attribution.html`)
- décision d'attribution (`decision_attribution.html`)
- report (`postpone.html`) 
- rejet (`rejection.html`)
Il est vivement conseillé d'avoir un template pour chaque situation, le bon fonctionnement de l'application ne peut être garanti autrement.

> [!WARNING]
> Les chemins de templates de notifications doivent être renseignés dans les objets fonds correspondants en base de données (champs de chemins) sous le format suivant : `FONDS/action.html` en fonction de l'arborescence définie au dessus.

## Contenus des différents PDFs et modification de ceux-ci

### Balises jinja

Les templates de PDF utilisent tous des balises jinja pour la gestion des contenus.
Merci de ne pas retirer ou modifier les balises suivantes ainsi que leur contenu, car elles sont essentielles à la génération des documents :
- `{% load ... %}` présentes en début de templates, elles permettent de charger les différents modules nécessaires à la génération des documents.
- `{% resolve %} {% endresolve %}` qui sont utilisées pour interpréter le contenu HTML présent en base de données.
- `{% if ... %} {% endif %}` qui servent aux conditions.
- `{% for ...%} {% endfor %}` qui servent aux boucles.
- `{{  }}` qui contiennent des variables utilisées pour retranscrire des informations stockées en base de données. 

#### Cas particulier : les balises de traductions

Au sein des différents templates se trouvent beaucoup de balises comme suit : 
```html
{% trans 'Associative project' %}
```
Ces balises sont utilisées pour les traductions des différents templates dans d'autres langues. 
La personnalisation des traductions n'étant pas encore disponibles, si l'une des correspondances ne convient pas, il est possible de changer le texte en effaçant complètement la balise et en la remplaçant par le texte brut souhaité.

A l'heure actuelle, seul le français est supporté, et s'il y a modification d'une traduction directement sur le template, elle ne tiendra pas compte de la locale utilisée.

Un tableau de correspondances des traductions sera bientôt mis à disposition au sein de la documentation.

### CSS

Les imports des différents fichiers CSS se présentent de la manière suivante au sein des templates : 
```html
<link rel="stylesheet" href="{% s3static 'css/exports/project_export.css' %}" type="text/css"/>
```
Il est tout à fait possible de modifier les fichiers CSS importés ou d'en ajouter de nouveaux, tant que le format de balise ci-dessus est strictement respecté (uniquement modifier le chemin vers le fichier CSS voulu).

Du moment que le lien vers le fichier de CSS existe dans le répertoire `css` de l'arborescence, il n'y a aucun nommage de fichier particulier à respecter, si ce n'est qu'il ne doit pas contenir d'espaces ou de caractères spéciaux.

Il est tout à fait possible d'adapter les différentes classes CSS utilisées sur les différents éléments du template si celles-ci on été définies dans le CSS customisé.

Dans certains templates une balise de style est définie : 
```html
        <style>
            @page {
                margin: 20mm 10mm 20mm 10mm;
                size: A4 portrait;
            }
        </style>
```
Au sein de cette balise, il est fortement déconseillé de modifier la partie `size: ` car elle définit le format et l'orientation du fichier de sortie. 
Le bon format de sortie des différents PDFs ne peut pas être garanti en cas de modification de cet attribut.
Les marges ou autres règles de style présentes au sein de ces mêmes balises peuvent en revanche être adaptées aux besoins.

### Images

Des imports d'images (à l'heure actuelle des logos) sont également présents dans les différents templates : 
```html
<img src="{% static 'img/unistra_logo.png' %}" alt="Université de Strasbourg">
```
De la même manière que pour l'import de fichiers CSS, il est tout à fait possible d'en ajouter ou d'en modifier, tant que le format de balise ci-dessus est strictement respecté (chemin vers l'image uniquement).
Il ne faut pas oublier de modifier l'alt des images en conséquence.

Du moment que le lien vers le fichier image existe dans le répertoire `img` de l'arborescence, il n'y a aucun nommage de fichier particulier à respecter, si ce n'est qu'il ne doit pas contenir d'espaces ou de caractères spéciaux.

### Spécificités des notifications

Ces fichiers se servent majoritairement de contenus html déjà stockés en base de données : objets `Contenu` dont le code commence par `NOTIFICATION_`.
Pour le bon fonctionnement de l'application, il faudra créer ces objets `Contenu` en fonction des différents fonds et actions. Leur code doit être formatté comme suit : 
```txt
NOTIFICATION_CODEFONDS_ACTION
```
Où `CODEFONDS` représente l'acronyme du fonds désiré en MAJUSCULES, et où `ACTION` peut être remplacé par le nom du template en MAJUSCULES et sans l'extension (`ATTRIBUTION` par exemple).
