---
title: Tests unitaires
weight: 217
---

## Configuration

L'application utilise [Vitest](https://vitest.dev/).

Il est possible de configurer la portée des tests et les options du *compiler* dans le fichier `tsconfig.vitest.json`.

## Portée

Les fichiers testés sont les stores et les composables.
La logique est, autant que possible, sortie des composants (hormis la gestion des erreurs HTTP).

Les tests sont placés dans les dossiers `__tests__` à la racine de `@/stores` et `@/composables`.

### *Fixtures*

Des *fixtures* sont disponibles dans le dossier `tests/fixtures`, pour simuler des jeux de données du backend.