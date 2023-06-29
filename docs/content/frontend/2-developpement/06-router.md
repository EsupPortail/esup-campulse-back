---
title: Router
weight: 216
---

## Structure

- Page d'accueil
- Associations (annuaire)
- Chartes
- Commissions (gestion des commissions et des projets, demandes de subventionnement, dépôts de bilan)
- Dashboard
- Connexion
- Création de compte
- Vues de gestion du mot de passe
- Contact
- À propos
- 404

## Configuration des *meta*

- `title` : titre `h1` de la vue affiché dans le `header`
- `breadcrumb` : fil d'Ariane pour la vue
- `colorVariant` : classe CSS permettant d'appliquer la bonne couleur pour l'espace concerné (uniquement pour l'élément parent)
- `requiresAuth` : indique si la vue nécessite une authentification (paramètre héréditaire)
- `associationMembersOnly` : indique si la vue est visible uniquement des utilisateurs membres d'une association (paramètre héréditaire)
- `staffOnly` : indique si la vue est visible uniquement des utilisateurs de groupes privés (paramètre héréditaire)

### Règles de redirection (*navigation guards*)

Par défaut, les requêtes n'aboutissant pas ou étant interdites (`403`) sont redirigées vers la page `404`. 
Les requêtes en mode non connecté nécessitant cependant une connexion sont redirigées vers la page `Login`. 
L'ensemble des règles mises en place sont visibles dans le fichier `@/router/index.ts`.
