---
title: Polices
weight: 222
---

# Variables SASS Personnalisées - Polices

## Variables
```scss
$baseFont   // Spécifie la famille de polices de base utilisée dans toute l'application.
$titleFont  // Spécifie la famille de polices pour les titres et les en-têtes.
```

## Ajout d'une Police Personnalisée

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

## Tailles de Police

Veuillez à vérifier la taille de votre police sur différentes tailles d'appareil.
```scss
$fontSize              // Définit la taille de police de base pour le contenu textuel général.
$headTitleMobileSize   // Définit la taille de police pour les titres et les en-têtes sur les appareils mobiles.
$headTitleComputerSize // Définit la taille de police pour les titres et les en-têtes sur les écrans d'ordinateur.
$titleSize             // Définit la taille de police pour les titres principaux et les en-têtes.
```