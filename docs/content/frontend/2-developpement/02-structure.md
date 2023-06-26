---
title: Structure
weight: 212
---

## Typage avec TypeScript

Le projet utilise le typage de [TypeScript](https://typescriptlang.org). L'ensemble des types et interfaces est défini dans des fichiers de types du dossier `types`.

## Gestion des erreurs HTTP

Par défaut, les erreurs HTTP sont gérées de la manière suivante :

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
La fonction `catchHTTPError` attrape les erreurs et notifie l'utilisateur selon le code d'erreur. Elle se trouve dans le composable `src/composables/useErrors.ts`.

## Router

Le router est utilisé pour naviguer entre les pages. On s'en sert également pour spécifier des paramètres par route, notamment :
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

Chaque grande section de l'application se démarque par une couleur distincte. Ces grandes parties sont les suivantes :
- Annuaire des associations.
- Espace CAPE.
- Espace chartes.
- Tableaux de bord.

Au niveau du router, le paramètre `colorVariant` défini dans `meta` permet d'appliquer la bonne classe CSS.

### Règles de redirection

Par défaut, les requêtes n'aboutisssant pas ou étant interdites (`403`) sont redirigées vers la page `404`. Les requêtes en mode non connecté nécessitant cependant une connexion sont redirigées vers la page `Login`. L'ensemble des règles mises en place sont visibles dans le fichier `@/router/index.ts`.

## Tests

L'application utilise [Vitest](https://vitest.dev/).

### Fixtures

Des fixtures sont disponibles dans le dossier `tests/fixtures`.

## Gérer les textes

Les textes sont à remplir dans le fichier `src/locales/fr.json`, dans l'ordre alphabétique. Ils peuvent être appelés comme suit : 

```vue
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

```nginx
add_header Content-Security-Policy "upgrade-insecure-requests; default-src 'none'; base-uri 'self'; child-src 'none'; connect-src 'self' https://plana-api-test.app.unistra.fr https://sentry.app.unistra.fr; font-src 'self'; frame-ancestors 'none'; frame-src 'none'; img-src 'self' data: https://s3.unistra.fr; manifest-src 'self'; media-src 'self'; object-src 'none'; script-src 'self'; style-src 'self'; worker-src 'self';";
```

### Autres directives

```nginx
add_header Access-Control-Allow-Origin "*"; # L'application autorise toutes les connexions.
add_header Referrer-Policy "same-origin"; # N'intègre pas d'information au sujet de l'application dans les headers HTTP pour les requêtes extérieures.
add_header Strict-Transport-Security "max-age=63072000"; # Autorise uniquement les connexions en HTTPS pour les 2 ans à venir.
add_header X-Content-Type-Options "nosniff"; # L'application appelle des fichiers de script et de style en vérifiant leur MIME-type. Cela permet d'éviter de détecter des scripts qui n'en sont pas.
add_header X-Frame-Options "DENY"; # N'autorise pas l'application à être embarquée dans une `<iframe>`.
```
