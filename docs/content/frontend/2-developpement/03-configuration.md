---
title: Configuration
weight: 213
---

## Nginx

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
- `object-src 'self'` : autorise uniquement les ressources intégrées sous la forme d'un élément `<object>` de l'application elle-même.
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

### Unsafe-eval

Des lignes ont été ajoutées dans le fichier `vite.config.ts` pour désactiver des scripts s'exécutant avec des unsafe-eval.

## ESLint

Quelques règles de lint mises en place dans le fichier `.eslintrc.json` :

- pas d'espace entre les `{}`
- quotes simples
- pas de `;`
- indentation à 4
- `ts-ignore` doit faire l'objet d'un commentaire
- les attributs des éléments HTML doivent aller à la ligne avec indentation

## Raccourcis

- `@` : redirige vers le dossier `./src`
- `#` : redirige vers le dossier `./types`
- `~` : redirige vers le dossier `./tests`