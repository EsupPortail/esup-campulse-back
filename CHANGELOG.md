# Changelog

## k8s-0.4.3 (27/07/2026)

### Features et évolutions
- Possibilité pour les superusers d'importer des données via des fichiers JSON pour les objets Association, ActivityField et Category (project) depuis l'interface Django Admin

### Corrections de bugs
- Correction de la génération des fichiers .zip de Projets dans une Commission lorsqu'il n'y a pas de fichier déposé pour les projets sélectionnés
- Les gestionnaires généraux peuvent à nouveau créer des contenus dans l'interface Django Admin

## k8s-0.4.2 (07/07/2026)

### Corrections de bugs
- Correction de l'encodage des noms de fichiers générés et retournés par l'API

## k8s-0.4.1 (03/07/2026)

### Features et évolutions
- Réduction de la longueur du champ Project "name" à 100 caractères maximum
- Les noms des fichiers générés par l'API sont désormais formattés et renvoyés de manière à être utilisés par un front

### Corrections de bugs
- Ajout du champ "id" dans le serializer de retour lors de la mise à jour des objets Content

### Autres changements
- Harmonisation du code pour l'envoi de mails (usage de la variable "current_site")

## k8s-0.4.0 (24/06/2026)

### Features et évolutions
- Nouveau filtre disponible sur les Commissions "to_postpone_project"
- Nouvelle route pour reporter un Projet dans une autre Commission

### Autres changements
- Optimisation du code pour des routes concernant les Commissions
- Optimisation du code pour des routes concernant les Users

## k8s-0.3.4 (22/06/2026)

### Features et évolutions
- Possibilité de personnaliser l'attribut CAS "uid" comme les autres attributs

### Corrections de bugs
- Lignes dupliquées dans l'admin django lors du tri par groupe sur la liste des utilisateurs
- Correction d'un bug empêchant le dépôt de charte lorsqu'elle est configurée en expiration par nombre de jours

### Configurations
- CI gitlab corrigée
- Configuration Sentry pour le PaaS

## k8s-0.3.3 (19/05/2026)

### Ajustements
- Restrictions plus strictes à la création de Users dans l'admin django pour les non super-utilisateurs
- Champ de contact blankable pour les Documents dans l'admin django

## k8s-0.3.2 (12/05/2026)

### Corrections de bugs
- Correction des noms et ids de Commissions présents lors de leur exports de liste de projets

## k8s-0.3.1 (27/04/2026)

### Corrections de bugs
- Correction des vérifications effectuées sur les documents nécessaires lors de la soumission de projet

## k8s-0.3.0 (21/04/2026)

### Features et évolutions
- Plus de détails sur les objets liés récupérés lors d'opérations sur des Project
- Mise à jour de la gestion des droits vis à vis des liens AssociationUser
- Mise à jour de la gestion des droits vis à vis des objets User

### Corrections de bugs
- Correction sur les fonds présents dans les documents d'exports de Commission

## k8s-0.2.7 (10/04/2026)

### Features et évolutions
- Un membre d'une association peut en voir les autres membres qui la constitue

## k8s-0.2.6 (09/04/2026)

### Features et évolutions
- L'inscription se fait désormais par une seule route qui combine tout en une (infos user, assos, groupes), pour utilisateur CAS ou local
- Route dédiée pour les DocumentUpload nécessaires à l'inscription
- Plus de détails sur les objets liés dans les routes de listes (associations, commissions, users...)
- Refactorisation des routes AssociationUser pour permettre une meilleure gestion des droits et des pré-filtrages dynamiques des données
- Le champ booléen Document "is multiple" est désormais un entier "max_uploads"
- Evolutions de l'admin django (permissions, champs obligatoires, correctifs variés)
 
### Configurations
- Correction des noms de variables CAS dans les settings docker
- Ajout de sonarqube dans la CI

### Autres changements
- Amélioration de la maintenabilité et de la lisibilité du code dans son ensemble
- Amélioration des performances globales de l'application
- Travail sur les permissions requises pour accéder aux routes d'API

## k8s-0.2.5 (21/11/2025)

### Correction de bugs
- Correction du templatetag "s3static" utilisé pour la personnalisation des templates pdfs

## k8s-0.2.4 (21/11/2025)

### Correction de bugs
- Correction de bug qui empêchait la bonne lecture des clés AGE lorsque lues depuis des fichiers

## k8s-0.2.3 (20/11/2025)

### Ajustements
- Nouveaux champs blankable pour les Documents dans l'admin
- Les clés AGE peuvent être utilisées depuis des variables d'environnement ou des fichiers comme avant

## k8s-0.2.2 (03/09/2025)

### Configurations
- Les clés AGE sont désormais des variables d'environnement non générées dans le docker-prestart

## 1.3.2 - k8s-0.2.1 (02/09/2025)

### Corrections de bugs
- Correction des permissions de l'admin Django pour la modification des templates de mails

### Features et évolutions
- Ajout d'une route de stats globales pour l'application

### Autres changements
- Optimisation des performances SQL de l'application

## 1.3.1 - k8s-0.2.0 (02/05/2025)

### Corrections de bugs
- Champs blankables dans l'admin django pour les associations

### Features et évolutions
- Génération de notifications d'attribution depuis l'admin django possible sur tous les environnements en tant que superuser
- MAJ de la documentation pour la personnalisation SaaS de l'application

## 1.3.0 (24/03/2025)

### Corrections de bugs

- Erreur 500 au report d'un projet dans une autre commission quand celui-ci n'avait pas de commentaire associé

### Features

- MAJ de la documentation de l'application
- Génération de PDF de notifications de test dans l'admin django
- Sauvegarde des vrais PDF de notifications dans S3
- Django admin adapté pour les utilisateurs du groupe Manager General

## 1.2.4 (27 Novembre 2024)

### Corrections de bugs

- Une adresse email ne peut pas être utilisée comme adresse de contact pour deux associations distinctes.

## 1.2.3 (17 Octobre 2024)

### Changements critiques

- Bascule sur un dépôt interne pour les packages `allauth_cas` et `britney`.

### Corrections de bugs

- Un projet peut ne plus avoir de responsable attitré si le responsable quitte l'association.
- Uniformisation du mode de calcul de la date de la charte.

### Autres changements

- Mise à jour du thème de la documentation technique (changement du submodule de `hugo-theme-learn` vers `hugo-theme-relearn`).

## 1.2.2 (09 Octobre 2024)

### Corrections de bugs

- Vérification supplémentaire de la casse de l'adresse mail à l'envoi du formulaire d'inscription.
- Optimisation des temps de réponse à l'appel des fonctions liées aux projets.

### Autres changements

- Meilleure gestion des erreurs avec Sentry.
- Nettoyage des librairies pour préparer une mise à jour majeure de django-allauth-cas et de britney.

## 1.2.1 (24 Septembre 2024)

### Corrections de bugs

- Vérification du fait qu'un document de projet ne peut pas être lié à un processus autre que celui d'un projet.
- Suppression du statut is_site à l'expiration d'une charte via la tâche Cron dédiée.

## 1.2.0 (17 Juillet 2024)

### Fonctionnalités

- Possibilité de modifier les paragraphes de contenu du site par un MANAGER_GENERAL.

### Changements critiques

- Permissions `view_project*_any_commission` renommées en `view_project*_any_fund`.
- Variable `CAS_INSTITUTION_ID` déplacée dans la base de données et renommée `CAS_INSTITUTION_ACRONYM` (renseigner désormais l'acronyme de l'établissement et non son identifiant).
- Variables de personnalisation usuelles désormais chargées dynamiquement via le Fabfile dans les configurations de déploiement ou via la table `contents_setting`.
- Changement du mode de rendu des templates PDF :
  - Suppression de la variable `TEMPLATES_NOTIFICATIONS`.
  - Nouveaux champs `*_template_path` dans le modèle `Fund` (migration nécessaire).
  - Stockage des templates et de leurs fichiers statiques sur S3 et dans un dépôt Git distinct.
- Retrait du support de Python 3.8, ajout du support de Python 3.12 (mais version 3.9 toujours conseillée).

### Corrections de bugs

- Correction des droits accordés à la délégation de présidence si une seule date est donnée.
- Correction des droits d'accès à un projet par un gestionnaire.
- Correction du non-envoi de mail de report de projet si aucun template n'est défini.
- Correction du bug de non-envoi de mail d'expiration des documents après un certain délai.
- Correction du bug d'affichage des blocs de texte sur le PDF de récap de bilan de projet.
- Correction du bug d'impossibilité de reporter les dates de projet d'une commission passée.
- Champs NULL autorisés sur la table Content.
- E-mails d'attribution des subventions envoyés uniquement aux gestionnaires concernés.
- Correction de la sélection des adresses mail de gestionnaires affichées par défaut dans les templates de mail.
- Changement de l'adresse no-reply des emails pour éviter les non-réceptions de mails.

### Autres changements

- Changement du mode de rendu des URLs des logos du pied de page et des associations.
- Modification des templates de mails relatifs à l'envoi d'un bilan de projet.
- Ajout du paramètre LDAP_ENABLED pour activer ou non l'ajout de compte via LDAP.
- Ajout des paramètres CAS_ATTRIBUTES_NAMES et CAS_ATTRIBUTES_VALUES pour gérer le mapping entre BDD et CAS.
- Ressources statiques chargées par la documentation Swagger autorisées dans la Content-Security-Policy.

## 1.0.0 (16 Novembre 2023)

- Stabilisation initiale de l'application.
