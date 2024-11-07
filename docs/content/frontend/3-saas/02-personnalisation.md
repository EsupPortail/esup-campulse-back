---
title: Personnalisation
weight: 312
---

## CSS

Il est possible de personnaliser les **couleurs**, les **polices** et les **tailles de police**.

Pour cela, il faut éditer le fichier `css/_custom.scss`.

Attention, seules les variables déclarées dans ce fichier seront prises en compte.
Tout CSS additionnel ne sera pas pris en compte.

### Couleurs de fond

```scss
$backgroundColor1      // Couleur de fond pour la zone de contenu principale.
$backgroundColor2      // Couleur de fond pour les zones de contenu secondaires.
$footerBackgroundColor // Couleur de fond pour la section du pied de page.
```

### Couleurs de texte

```scss
$footerTextColor              // Couleur du texte dans la section du pied de page.
$textColor1, $textColor2, ..  // Définissent différentes couleurs de texte utilisées dans toute l'application.
```

Les couleurs sont regroupées en 4 groupes représentant chacun un module de l'application : 

- Le module associations
- Le module des chartes
- Le module commissions
- Le tableau de bord

Elles peuvent être identiques ou différentes, comme c'est le cas pour l'Université de Strasbourg.

```scss
$associationColor // Couleur associée aux éléments liés aux associations.
$charterColor     // Couleur associée aux éléments liés aux chartes.
$commissionColor  // Couleur associée aux éléments liés aux commissions.
$dashboardColor   // Couleur associée aux éléments liés au tableau de bord.
```

Les tailles de polices doivent être déclarées en unités relatives.

## Polices

Les polices peuvent être modifiées en étant déclarées au préalable dans le fichier `css/_fonts` et déposées dans le dossier `fonts`.

### Variables

```scss
$baseFont   // Spécifie la famille de polices de base utilisée dans toute l'application.
$titleFont  // Spécifie la famille de polices pour les titres et les en-têtes.
```

### Ajout d'une police personnalisée

Pour utiliser une police personnalisée, elle doit être importée dans le fichier `_fonts.scss`.
Exemple ci-dessous :

```scss
// Importation de la police Titillium Web, en style normal et épaisseur légère

/* latin-ext */
@font-face {
  font-family: 'Titillium Web';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url('fonts/Titillium_Web/TitilliumWeb-300-Latin-ext.woff2') format('woff2');
  unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;
}

/* latin */
@font-face {
  font-family: 'Titillium Web';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url('fonts/Titillium_Web/TitilliumWeb-300-Latin.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
```

```scss
$baseFont: 'Titillium Web', sans-serif;
```

### Tailles de police

Veillez à vérifier la taille de votre police sur différentes tailles d'appareil.

```scss
$fontSize              // Définit la taille de police de base pour le contenu textuel général.
$headTitleMobileSize   // Définit la taille de police pour les titres et les en-têtes sur les appareils mobiles.
$headTitleComputerSize // Définit la taille de police pour les titres et les en-têtes sur les écrans d'ordinateur.
$titleSize             // Définit la taille de police pour les titres principaux et les en-têtes.
```

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

Les textes du thème sont disponibles sur le [portail ESUP](https://github.com/EsupPortail/esup-campulse-front/blob/main/src/locales/fr.json).

Il est possible de modifier les textes (uniquement les valeurs, pas les clés).

Les textes ont été initialement rédigés pour l'Université de Strasbourg.
Bien qu'un travail d'unification ait été réalisé, il est possible qu'il reste des tournures qui pourraient ne pas correspondre à tous les établissements.

Commencez par vérifier et personnaliser si besoin les textes suivants : 

```txt
university-name
charter.site.name
forms.gdpr-consent
cape
project.recap
accessibility-declaration
```

Assurez-vous également de contrôler les références à ces textes.
Les références sont appelées ainsi : `@:voici-une-référence`.

Pour écraser un texte, ajoutez-le dans `locales/custom.txt`.

Attention à bien respecter cette syntaxe (clé=texte, sans guillemets et saut de ligne) : 

```txt
university-name=Université de la Réunion
```