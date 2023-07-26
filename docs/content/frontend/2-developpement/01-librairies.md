---
title: Librairies
weight: 211
---

## Librairies et frameworks

- [vue](https://www.npmjs.com/package/vue) : framework général.
- [@sentry/vue](https://www.npmjs.com/package/@sentry/vue) : bug reporting.
- [axios](https://www.npmjs.com/package/axios) : requêtes vers l'API.
- [bootstrap-icons](https://www.npmjs.com/package/bootstrap-icons) : icônes.
- [pinia](https://www.npmjs.com/package/pinia) : store de données.
- [quasar](https://www.npmjs.com/package/quasar) : framework de composants.
- [vue-i18n](https://www.npmjs.com/package/vue-i18n) : traduction.
- [vue-router](https://www.npmjs.com/package/vue-router) : routing.
- [zxcvbn](https://www.npmjs.com/package/zxcvbn) : estimation de la force d'un mot de passe.
- [@vue-unistra/cas-authentication](https://git.unistra.fr/vue-unistra/cas-authentication) : plugin d'authentification vers CAS.

## Utilitaires de développement

- [@intlify/unplugin-vue-i18n](https://www.npmjs.com/package/@intlify/unplugin-vue-i18n) : optimisation du plugin de traductions pour le bundler.
- [@pinia/testing](https://www.npmjs.com/package/@pinia/testing) : suite de tests pour le store de données.
- [@quasar/vite-plugin](https://www.npmjs.com/package/@quasar/vite-plugin) : optimisation du framework de composants pour le bundler.
- [@types/jsdom](https://www.npmjs.com/package/@types/jsdom) : types pour Javascript.
- [@types/node](https://www.npmjs.com/package/@types/node) : types pour Node.
- [@types/zxcvbn](https://www.npmjs.com/package/@types/zxcvbn) : types pour zxcvbn.
- [@vitejs/plugin-vue](https://www.npmjs.com/package/@vitejs/plugin-vue) : optimisation du framework pour le bundler.
- [@vitest/coverage-c8](https://www.npmjs.com/package/@vitest/coverage-c8) : couverture des tests.
- [@vitest/ui](https://www.npmjs.com/package/@vitest/ui) : interface graphique de la suite de tests.
- [@vue/eslint-config-typescript](https://www.npmjs.com/package/@vue/eslint-config-typescript) : optimisation du linter pour TypeScript.
- [@vue/test-utils](https://www.npmjs.com/package/@vue/test-utils) : suite de tests pour le framework.
- [@vue/tsconfig](https://www.npmjs.com/package/@vue/tsconfig) : optimisation de TypeScript pour le framework.
- [eslint](https://www.npmjs.com/package/eslint) : linter.
- [eslint-plugin-vue](https://www.npmjs.com/package/eslint-plugin-vue) : optimisation du linter pour le framework.
- [jsdom](https://www.npmjs.com/package/jsdom) : DOM Javascript.
- [sass](https://www.npmjs.com/package/sass) : Sass.
- [typescript](https://www.npmjs.com/package/typescript) : TypeScript.
- [vite](https://www.npmjs.com/package/vite) : bundler.
- [vitest](https://www.npmjs.com/package/vitest) : tests unitaires.
- [vue-tsc](https://www.npmjs.com/package/vue-tsc) : vérification des types.

## Notes sur les dépendances

### Vue

Framework général de l'application, en version 3. 
L'application utilise l'[API de composition](https://vuejs.org/guide/introduction.html#api-styles) et [`script setup`](https://vuejs.org/api/sfc-script-setup.html).

### vue-unistra/cas-authentication

Plugin d'authentification avec CAS pour une application frontend en Vue, développé à l'Unistra.
Permet notamment de gérer le refresh automatique des tokens d'authentification expirés.

[Accéder au dépôt](https://git.unistra.fr/vue-unistra/cas-authentication)

### Axios

Gère les requêtes vers l'API. 

Plus d'informations sur la configuration d'Axios sont disponibles sur la page "Structure".

### Pinia

[Pinia](https://pinia.vuejs.org/) permet de gérer des stores avec Vue.

### Quasar

Librairie de composants pour Vue. Divers composants sont utilisés à travers l'application, notamment les éléments de formulaire et les tableaux (QTable).

Les composants Quasar sont configurés pour être importés et fonctionner en PascalCase (`vite.config.ts`).

2 API Quasar spécifiques sont également utilisées :
- Notify.
- Loading.

[Consulter la documentation](https://quasar.dev/docs)

#### Notify

L'[API Notify](https://quasar.dev/quasar-plugins/notify#notify-api) est un plugin de Quasar qui permet d'afficher des messages animés flottant au bas de l'écran pour informer les utilisateurs sous forme de notification. Notify s'utilise comme suit : 

```js
notify({
    type: 'positive',
    message: 'You are successfully logged in!'
})
```

#### Loading

L'[API Loading](https://quasar.dev/quasar-plugins/loading#loading-api) de Quasar est une fonctionnalité qui permet d'afficher un overlay grisé sur l'écran indiquant à l'utilisateur qu'une tâche est en train de s'effectuer en arrière-plan et qu'il doit patienter. Loading s'utilise comme suit sur l'ensemble des fonctions asynchrones : 

```js
loading.show()
await yourAsyncFunction()
loading.hide()
```

### Vue I18n

[Vue I18n](https://vue-i18n.intlify.dev/) est un plugin d'internationalisation pour Vue.

Plus d'informations sur la configuration d'Axios sont disponibles sur la page "I18n".

### Vue Router

[Vue Router](https://router.vuejs.org/) permet de naviguer entre les différentes vues de l'application.

Plus d'informations sur la configuration d'Axios sont disponibles sur la page "Router".

### Bootstrap Icons

[Bootstrap Icons](https://icons.getbootstrap.com/) est une librairie d'icônes.

Elles sont intégrées sous forme d'icônes avec l'élément `<i>` ou dans des éléments Quasar le permettant avec un attribut `icon`.
