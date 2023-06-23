---
title: Tâches CRON
weight: 107
---

Les différentes commandes exécutables via des tâches CRON se trouvent dans le répertoire `plana/management/commands` du dépôt, avec les commandes personnalisées d'aide au développement :
- `account_expiration` (suppression des comptes après un an d'inactivité).
- `association_expiration` (changement de statut de la charte des associations qui vient à expirer ou expire).
- `commission_expiration` (suppression des liens entre brouillons de projets et dates de commissions expirées).
- `document_expiration` (changement de statut des documents (chartes de subventionnement) qui viennent à expirer ou expirent).
- `goa_expiration` (liste des associations dont la date de dernière Assemblée Générale Ordinaire a plus de 11 mois).
- `password_expiration` (réinitialisation des mots de passe après un an sans changement).
- `project_expiration` (suppression des projets vieux de dix ans).
- `review_expiration` (rappel de soumettre le bilan d'un projet subventionné).

Il est également possible de lancer ces commandes manuellement via `$ python manage.py NOM_DE_LA_COMMANDE`.
