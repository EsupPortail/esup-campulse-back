---
title: Variables personnalisées
weight: 221
---

# Variables SASS Personnalisées

Le but du fichier _custom.scss est de permettre aux utilisateurs de personnaliser différents aspects du style de l'application en ajustant des variables SASS prédéfinies. 

# Modification des Variables

Pour personnaliser le style de l'application, les utilisateurs peuvent modifier les variables suivantes définies dans le fichier _custom.scss

## Polices
```scss
$baseFont   // Spécifie la famille de polices de base utilisée dans toute l'application.
$titleFont  // Spécifie la famille de polices pour les titres et les en-têtes.
```

### Tailles de Police
```scss
$fontSize              // Définit la taille de police de base pour le contenu textuel général.
$headTitleMobileSize   // Définit la taille de police pour les titres et les en-têtes sur les appareils mobiles.
$headTitleComputerSize // Définit la taille de police pour les titres et les en-têtes sur les écrans d'ordinateur.
$titleSize             // Définit la taille de police pour les titres principaux et les en-têtes.
```

## Couleurs

### Couleurs de Fond
```scss
$backgroundColor1      // Couleur de fond pour la zone de contenu principale.
$backgroundColor2      // Couleur de fond pour les zones de contenu secondaires.
$footerBackgroundColor // Couleur de fond pour la section du pied de page.
```

### Couleurs de Texte
```scss
$footerTextColor              // Couleur du texte dans la section du pied de page.
$textColor1, $textColor2, ..  // Définissent différentes couleurs de texte utilisées dans toute l'application.

```
## Variables de Couleur Spécifiques Personnalisées

Les variables alliées à 'association', 'charter', 'commission' et 'dashboard' définissent les couleurs associées aux sections appropriées de l'application. 

```scss
$associationColor // Couleur associée aux éléments liés aux associations.
$charterColor     // Couleur associée aux éléments liés aux chartes.
$commissionColor  // Couleur associée aux éléments liés aux commissions.
$dashboardColor   // Couleur associée aux éléments liés au tableau de bord.
```
