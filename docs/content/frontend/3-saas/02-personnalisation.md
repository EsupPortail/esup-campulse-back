---
title: Personnalisation
weight: 312
---

Le dépôt de personnalisation se présente sous cette forme :

```txt
├── css
├── favicon.ico
├── fonts
├── images
├── locales
└── opengraph-image.jpg
```

## CSS

Il est possible de personnaliser les **couleurs**, les **polices** et les **tailles de police**.

Pour cela, il faut éditer le fichier `css/_custom.scss`.

Attention, seules les variables déclarées dans ce fichier seront prises en compte.
Tout CSS additionnel ne sera pas pris en compte.

Les couleurs sont regroupées en 4 groupes représentant chacun un module de l'application : 

- Le module associations
- Le module des chartes
- Le module commissions
- Le tableau de bord

Elles peuvent être identiques ou différentes, comme c'est le cas pour l'Université de Strasbourg.

Les tailles de polices doivent être déclarées en unités relatives.

## Polices

Les polices peuvent être modifiées en étant déclarées au préalable dans le fichier `css/_fonts` et déposées dans le dossier `fonts`.

## Images

**Remarques importantes :**

- Attention à bien respecter le nommage et le format des fichiers. S'ils sont mal nommés ou dans un mauvais format, ils ne seront pas pris en compte par le thème.
- Redimensionner et compresser les images pour ne pas alourdir les pages.

### Images du thème

Les images du thème sont à modifier dans le dossier `/images`.

- Page d'accueil : `background-cape.jpg`, `background-charter.jpg`, `background-directory.jpg`
- Bannière d'en-tête : `background-header.jpg`
- Page `/charter` : `charter-image-1.jpg`, `charter-image-2.jpg`, `charter-image-3.jpg`
- Page `/commission`: `commission-image-1.jpg`, `commission-image-2.jpg`
- Page `/associations` : `directory-image.jpg`
- Logo par défaut des associations : `no_logo_square.png`

### Image opengraph

`opengraph-image.jpg` est l'image utilisée pour le balisage *Opengraph*.

Elle se situe à la racine du dépôt.

### Favicon

`favicon.ico` est l'image utilisée en favicon.

Elle se situe à la racine du dépôt.

## Textes du thème

Les textes du thème sont disponibles dans le dossier `/locales`, dans le fichier `fr.json`.

Il est possible de modifier les textes (uniquement les valeurs, pas les clés).

Les textes ont été initialement rédigés pour l'Université de Strasbourg.
Bien qu'un travail d'unification a été réalisé, il est possible qu'il reste des tournures qui pourraient ne pas correspondre à tous les établissements.

Commencez par vérifier et personnaliser si besoin les textes suivants : 

```txt
university-name
charter.site.name
forms.gdpr-accept
forms.gdpr-data-controller
cape
project.recap
accessibility-declaration
```

Assurez-vous également de contrôler les références à ces textes.
Les références sont appelées ainsi : `@:voici-une-référence`.

Pour écraser un texte, créez un fichier `custom.txt` que vous placerez dans le dossier `locales`.

Attention à bien respecter cette syntaxe (clé=texte, sans guillemets et saut de ligne) : 

```txt
university-name=Université de la Réunion
```