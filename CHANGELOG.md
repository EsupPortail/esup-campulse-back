# Changelog

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
