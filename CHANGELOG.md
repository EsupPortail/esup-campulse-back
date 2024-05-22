# Changelog

## 1.1.0 (Q2 2024)

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
