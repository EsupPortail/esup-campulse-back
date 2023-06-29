---
title: Layouts et styles
weight: 219
---

## Gestion des layouts

L'application utilise 2 layouts :

- `LayoutDefault.vue`, utilisé sur la quasi-totalité des pages.
- `LayoutMinimalHeader.vue`, utilisé sur certaines pages uniquement comme `Login` et `404`.

L'utilisation de ces layouts est définie dans le router.

## Gestion des couleurs par espace

Chaque grande section de l'application se démarque par une couleur distincte. Ces grandes parties sont les suivantes :

- annuaire des associations
- espace commissions
- espace chartes
- tableaux de bord

Au niveau du router, le paramètre `colorVariant` défini dans `meta` permet d'appliquer la bonne classe CSS.

## Titres `h1`

- titres statiques : configurés dans les options `meta` de la route
- titres dynamiques : configurés au niveau de la vue via la variable réactive `dynamicTitle` (`useUtility.ts`)