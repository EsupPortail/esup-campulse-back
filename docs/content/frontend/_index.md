---
title: Documentation du Frontend
weight: 10
---

## Version de Vue

Vue est en version 3.

L'application utilise l'[API de composition](https://vuejs.org/guide/introduction.html#api-styles) et [`script setup`](https://vuejs.org/api/sfc-script-setup.html).

## Variables d'environnement

Les variables d'environnement nécessaires sont les suivantes :

```
NODE_ENV=development
VITE_APP_SITE_NAME=Opaline
VITE_APP_BASE_URL=http://localhost:8000
VITE_APP_FRONT_URL=http://localhost:3000
VITE_APP_CAS_URL=YourCASUrl
VITE_APP_I18N_LOCALE=fr
```

## Dépendances

### vue-unistra/cas-authentication

Plugin d'authentification avec CAS pour une application front en Vue.
Permet notamment de gérer le refresh automatique des tokens expirés.

[Accéder au dépôt](https://git.unistra.fr/vue-unistra/cas-authentication)

### Axios

Permet de faire des requêtes à l'API.

2 instances d'Axios sont en place dans `@/composables/useAxios.ts` :

- `axiosPublic` pour gérer les requêtes publiques, sans authentification.
- `axiosAuthenticated` pour gérer les requêtes privées, avec authentification. Dans ce cas, les fonctions de `vue-unistra/cas-authentication` s'exécutent, notamment pour gérer le refresh des tokens.

Attention à bien utiliser la bonne instance. Une requête publique effectuée avec l'instance privée peut générer une erreur. 

### Quasar

Librairie de composants pour Vue. 

[Consulter la documentation](https://quasar.dev/docs)

Divers composants sont utilisés à travers l'application, notamment les éléments de formulaire et les tableaux (QTable).

La [librairie d'icônes](https://quasar.dev/options/quasar-icon-sets) utilisée pour les éléments Quasar spécfiquement est [MDI](https://pictogrammers.com/library/mdi/).

2 API Quasar spécifiques sont également utilisées :

- Notify.
- Loading.

#### Notify

L'[API Notify](https://quasar.dev/quasar-plugins/notify#notify-api) est un plugin de Quasar qui permet d'afficher des messages animés flottant au bas de l'écran pour informer les utilisateurs sous forme de notification.

Notify s'utilise comme suit : 

```
notify({
    type: 'positive',
    message: 'You are successfully logged in!'
})
```

#### Loading

L'[API Loading](https://quasar.dev/quasar-plugins/loading#loading-api) de Quasar est une fonctionnalité qui permet d'afficher un overlay grisé sur l'écran indiquant à l'utilisateur qu'une tâche est en train de s'effectuer en arrière plan et qu'il doit patienter.

Loading s'utilise comme suit sur l'ensemble des fonctions asynchrones : 

```
loading.show()
await yourAsyncFunction()
loading.hide()
```

### Pinia

[Pinia](https://pinia.vuejs.org/) permet de gérer des stores avec Vue.

### Vue Router

[Vue Router](https://router.vuejs.org/) permet de naviguer entre les différentes vues de l'application.

### Vue I18n

[Vue I18n](https://vue-i18n.intlify.dev/) est un plugin d'internationalisation pour Vue.

### Bootstrap Icons

[Bootstrap Icons](https://icons.getbootstrap.com/) est une librairie d'icônes.

Elles sont intégrées sous forme d'icônes avec l'élement `<i>`.

## Typage avec TypeScript

Le projet utilise le typage de [TypeScript](https://typescriptlang.org).

L'ensemble des types et interfaces est défini dans des fichiers de types, dans `@/types`.

## Gestion des erreurs HTTP

Par défaut, les erreurs HTTP sont gérées de la manière suivante :

```
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
La fonction `catchHTTPError` attrape les erreurs et notifie l'utilisateur selon le code d'erreur. 
Elle se trouve dans le composable `@/composable/useErrors.ts`.

## Router

Le router est utilisé pour naviguer entre les pages.

On s'en sert également pour spécifier des paramètres par route, notamment :

- Titres.
- Intitulés des breadcrumbs.
- Classes CSS.
- Autorisations.

### Gestion des layouts

L'application utilise 2 layouts :

- `LayoutDefault.vue`, utilisé sur la quasi-totalité des pages.
- `LayoutMinimalHeader.vue`, utilisé sur certaines pages uniquement comme `Login` et `404`.

L'utilisation de ces layouts est définie dans le router.

### Gestion des couleurs par espace

Chaque grande section de l'application se démarque par une couleur distincte.

Ces grandes parties sont les suivantes :

- Annuaire des associations.
- Espace CAPE.
- Espace chartes.
- Tableaux de bord.

Au niveau du router, le paramètre `colorVariant` défini dans `meta` permet d'appliquer la bonne classe CSS.

### Règles de redirection

Par défaut, les requêtes n'aboutisssant pas ou étant interdites (`403`) sont redirigées vers la page `404`.

Les requêtes en mode non connecté nécessitant cependant une connexion sont redirigées vers la page `Login`.

L'ensemble des règles mises en place sont visibles dans le fichier `@/router/index.ts`.

## Tests

L'application utilise [Vitest](https://vitest.dev/).

### Fixtures

Des fixtures sont disponibles dans le dossier `@/tests/fixtures`.

## Gérer les textes

Les textes sont à remplir dans le fichier `@/locales/fr.json`, dans l'ordre alphabétique.

Ils peuvent être appelés comme suit : 

```
<script lang="ts" setup>
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
</script>

<template>
    <p>{{ t('hello-world') }}</p>
</template>
```

## Configuration NGINX

Une configuration de sécurité basique est mise en place au niveau du serveur Nginx. 


### Content-Security-Policy

L'en-tête de réponse HTTP Content-Security-Policy permet de contrôler les ressources que l'application est autorisée à charger pour une page donnée.

- `upgrade-insecure-requests` : redirige toutes les requêtes vers HTTPS.
- `default-src 'none'` : fallback pour tous les types de requêtes. Par défaut, toutes les requêtes sont refusées.
- `base-uri 'self'` : autorise uniquement sa propre URI comme base.
- `connect-src 'self' https://plana-api-test.app.unistra.fr https://sentry.app.unistra.fr` : autorise uniquement les requêtes vers l'application elle-même, vers l'API, et l'outil de monitoring Sentry.
- `font-src 'self'` : autorise uniquement le chargement des polices d'écriture de l'application elle-même.
- `frame-ancestors 'none'` : n'autorise pas les sites tiers à embarquer l'application sous forme d'`<iframe>`.
- `frame-src 'none'` : n'autorise aucun contenu embarqué sous forme d'`<iframe>` sur l'application.
- `img-src 'self' data: https://s3.unistra.fr` : autorise uniquement le chargement des images de l'application elle-même, en base64, et en provenance de S3 (logos des associations).
- `manifest-src 'self'` : autorise le manifeste de PWA à se charger.
- `media-src 'self'` : autorise uniquement le chargement de médias de l'application elle-même.
- `object-src 'self'` : autorise uniquement les ressources intégrées sous la forme d'un élement `<object>` de l'application elle-même.
- `script-src 'self'` : autorise uniquement l'exécution des scripts de l'application elle-même.
- `style-src 'self'` : autorise uniquement le chargement des styles de l'application elle-même.
- `worker-src 'self'` : autorise uniquement l'exécution des workers de l'application elle-même.

```
add_header Content-Security-Policy "upgrade-insecure-requests; default-src 'none'; base-uri 'self'; child-src 'none'; connect-src 'self' https://plana-api-test.app.unistra.fr https://sentry.app.unistra.fr; font-src 'self'; frame-ancestors 'none'; frame-src 'none'; img-src 'self' data: https://s3.unistra.fr; manifest-src 'self'; media-src 'self'; object-src 'none'; script-src 'self'; style-src 'self'; worker-src 'self';";
```

### Access-Control-Allow-Origin

L'application autorise toutes les connexions.

```
add_header Access-Control-Allow-Origin "*";
```

### Referrer-Policy

N'intègre pas d'information au sujet de l'application dans les headers HTTP pour les requêtes extérieures.

```
add_header Referrer-Policy "same-origin";
```

### Strict-Transport-Security

Autorise uniquement les connexions en HTTPS pour les 2 ans à venir.

```
add_header Strict-Transport-Security "max-age=63072000";
```  

### X-Content-Type-Options

L'application appelle des fichiers de script et de style en vérifiant leur MIME-type. Cela permet d'éviter de détecter des scripts qui n'en sont pas.

```
add_header X-Content-Type-Options "nosniff";
```

### X-Frame-Options

N'autorise pas l'application à être embarquée dans une `<iframe>`.

```
add_header X-Frame-Options "DENY";
```

### X-XSS-Protection

Bloque le chargement des pages lorsque le navigateur détecte une attaque XSS reflétée (lorsqu'une application reçoit des données dans une requête HTTP et les inclut dans la réponse immédiate d'une manière non sécurisée). 

```
add_header X-XSS-Protection "1; mode=block";
```
