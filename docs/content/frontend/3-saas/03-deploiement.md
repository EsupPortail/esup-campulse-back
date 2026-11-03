---
title: Déclencher le déploiement
weight: 313
---

Pour rappel, à chaque publication (push) sur le dépôt le déploiement est automatiquement déclenché. 
Une modification (push) standard initie un déploiement en préproduction, tandis qu’un push tagué déclenche un déploiement en préproduction et en production.

Autrement dit, pour déployer en production, il faut nécessairement créer un tag.

## Qu’est-ce qu’un tag ?

Un **tag** est une étiquette que l’on pose sur une version de l’application pour indiquer :
"Cette version est validée et prête à aller en production".

Dans notre projet, **créer un tag = déclencher automatiquement le déploiement en production**.

**Attention** : il ne faut créer un tag qu’une fois les tests réalisés et validés sur la préproduction.

## Comment nommer un tag ?

Pour simplifier, nous utilisons **la date du jour** comme nom de tag.

* Format recommandé : `AAAA-MM-JJ` (exemple : `2025-09-02`).
* En cas de déploiements multiples la même journée : `2025-09-02-2` puis `2025-09-02-3` et ainsi de suite.
* Cela permet de savoir rapidement quand la version a été déployée.

## Créer un tag

Vous pouvez réaliser l'opération en ligne de commande ou directement dans l'interface web de votre dépôt.
Selon que vous utilisiez GitLab ou GitHub, la méthode diffère légèrement.


### Créer un tag sur l'interface **GitLab**

1. Ouvrir le projet sur GitLab.
2. Aller dans **Repository > Tags**.
3. Cliquer sur **New tag**.
4. Dans **Tag name**, écrire la date du jour (ex. `2025-09-02`).
5. Dans **Create from**, choisir la branche `main`.
6. Cliquer sur **Create tag**.

Le déploiement démarre automatiquement.

### Créer un tag sur l'interface **GitHub**

1. Ouvrir le projet sur GitHub.
2. Aller dans l’onglet **Releases**.
3. Cliquer sur **Create a new release**.
4. Dans **Select tag**, écrire la date du jour (ex. `2025-09-02`).
5. Sélectionner la branche `main` dans **Target**.
6. Cliquer sur **Publish release**.

Le déploiement démarre automatiquement.

## Créer un tag en **ligne de commande** (option avancée)

```bash
# Depuis le dossier du projet
git tag -a 2025-09-02 -m "Version validée du 2 septembre 2025"
git push origin 2025-09-02
```

Le déploiement démarre automatiquement.

## À retenir

* Le tag déclenche le **déploiement en production**.
* Toujours vérifier que la version est **testée et validée en préproduction** avant de créer un tag.
* Utiliser la **date du jour** comme nom de tag.
