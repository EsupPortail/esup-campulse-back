---
title: Base de données
weight: 122
---

Un ensemble de données minimal doit être ajouté en base de données pour assurer le bon fonctionnement de l'application. Ces données peuvent être modifiées par le superutilisateur de l'application à l'adresse `https://URL_DU_BACK/admin/` :
- Comptes gestionnaires à ajouter à l’application (`User` : nom, prénom, adresse mail, groupe de gestionnaire).
- Établissements auxquels peuvent se rattacher les associations (`Institution` : nom, acronyme).
- Composantes de ces établissements (`InstitutionComponent` : nom, établissement de rattachement).
- Domaines d’activité que peut avoir une association (`ActivityField` : nom).
- Fonds de subventionnement (`Fund` : nom, acronyme, établissement de rattachement issu de la liste précédente).
- Documents attendus dans les différents process (`Document` : type de fichier (image, PDF, tableur, ...), plusieurs fichiers autorisés pour ce document ou non, dépôt obligatoire ou non, fonds de rattachement ou non, date d’expiration ou non).
- Contenus textuels (`Content` : tous les paragraphes visibles sur le site sans être connecté).
- Liste des logos du pied de page (`Logo` : image, titre, acronyme, URL de redirection, position).
- Sujets et corps de texte des emails envoyés (`MailTemplate` : nom, sujet, corps de texte).
