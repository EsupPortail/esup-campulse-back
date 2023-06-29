---
title: Structure
weight: 215
---

## Vues

- vues à la racine du dossier : page d'accueil, réinitiatlisation du mot de passe, contact, à propos, etc.
- dossier `charter` : gestion et signature des chartes
- dossier `commission` : gestion des commissions
- dossier `dashboard` : tableaux de bord, espaces de gestion du compte, etc.
- dossier `directory` : annuaire des associations
- dossier `project` : demandes de subvention et projets

## Composants

- `alert` : boîtes de dialogue pour confirmer des actions
- `charter` : composants pour les chartes
- `commission` : composants pour les commissions
- `document` : composants pour la gestion et l'upload de documents
- `form` : formulaires transversaux
- `infoPanel` : éléments de layout pour donner des informations
- `layout` : éléments de layout du thème
- `project` : composants pour les projets

## Stores

- `useAssociationStore` : gestion du state pour les associations et leurs données associées (établissements, composantes, domaines d'activités, membres, etc.)
- `useContentStore` : gestion du state pour les contenus récupérés via l'API
- `useProjectStore` : gestion du state pour les projets, les bilans et leurs données associées (catégories, fonds, documents, etc.)
- `useUserManagerStore` : gestion du state pour les utilisateurs gérés par les gestionnaires
- `useUserStore` : gestion du state pour les données de l'utilisateur connecté (logIn, logOut, etc.)

## Composables

### Composables 

Les composables regroupent des fonctions plus complexes que les stores pour des points précis : 

- `useAssociations.ts` : gestion des associations
- `useAxios.ts` : configuration d'Axios (plugin pour les appels API)
- `useCharters.ts` : gestion des chartes
- `useColorVariants` : gestion du style en fonction des vues
- `useCommissions.ts` : gestion des commissions
- `useDirectory.ts` : gestion de l'annuaire des associations
- `useDocumentUploads.ts` : upload de documents
- `useDocuments.ts` : gestion de la librairie de documents
- `useErrors.ts` : gestion des erreurs HTTP
- `useProjectComments.ts`: gestion des commentaires
- `useSecurity.ts` : fonctions liées à l'authentification et à la sécurité
- `useSubmitProject.ts` : gestion de la demande de subventionnement
- `useSubmitReview.ts` : gestion du dépôt de bilan
- `useUserAssociations.ts` : gestion des membres d'association
- `useUserGroups.ts` : gestion des droits
- `useUsers.ts` : gestion des utilisateurs de l'application par les gestionnaires
- `useUtility.ts` : fonctions utilitaires configurables, regex, dates, etc.

### Cas particuliers 

#### useAxios.ts

- Deux instances d'Axios sont en place dans `@/composables/useAxios.ts` :

- `axiosPublic` pour gérer les requêtes publiques, sans authentification.
- `axiosAuthenticated` pour gérer les requêtes privées, avec authentification et `vue-unistra/cas-authentication`.

Attention à bien utiliser la bonne instance. Une requête publique effectuée avec l'instance privée peut générer une erreur.

#### useErrors.ts

Les erreurs HTTP peuvent être levées et affichées à l'utilisateur de la manière suivante :

```js
try {
    // some code
} catch (error) {
    if (axios.isAxiosError(error) && error.response) {
        notify({
            type: 'negative',
            message: t(`notifications.negative.${catchHTTPError(error.response.status)}`)
        })
    }
}
```

#### useColorVariants.ts

Application du style en fonction de la route.
Plus d'information sur les pages "Router" et "Layouts et styles".

#### useSecurity.ts

- `hasPerm` : vérifie si l'utilisateur a la permission passée en argument. Se base sur les permissions renvoyées par l'API avec les données de l'utilisateur.
- `checkPasswordStrength` : vérifie la force d'un mot de passe. Se base sur la librairie zxcvb.

#### useUserGroups.ts

- `groupChoiceLimit` : nombre de groupes qu'un utilisateur peut rejoindre. Par défaut défini à 2.
- `groupNames` : permet de transcrire les noms de code des groupes du back-end en noms littéraux. À compléter en cas d'ajout de groupe.
- `canJoinAssociationGroups` : liste les groupes autorisés à rejoindre une association.
- `initStaffStatus` et `isStaff` : détermine si le groupe est public ou non (généralement pour les gestionnaires et les admins).

#### useUtility.ts

- `CURRENCY` : définit la devise (pour les formulaires et les récapitulatifs de demandes de subventionnement et les bilans).