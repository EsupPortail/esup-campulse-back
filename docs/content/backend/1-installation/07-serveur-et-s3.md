---
title: Serveur et S3
weight: 107
---

## Déploiement de l'application

L'application a été initialement pensée pour être déployée avec [Fabric](https://www.fabfile.org/) et [Pydiploy](https://pypi.org/project/pydiploy/). Des exemples de configuration sont disponibles dans le dossier `fabfile`.

Le fichier contient également un exemple de Content-Security-Policy pouvant être appliqué (au format Nginx), prenant en compte les ressources chargées par django-admin :

```nginx
add_header Content-Security-Policy "upgrade-insecure-requests; default-src 'none'; base-uri 'self'; connect-src 'self'; font-src 'self' https://stackpath.bootstrapcdn.com; frame-ancestors 'self'; frame-src 'self'; img-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://stackpath.bootstrapcdn.com; style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com;";
```

## Mise en place du serveur S3

Deux buckets S3 sont utilisés pour stocker les différents types de documents, un bucket est public et l'autre est privé.

Dans le bucket public sont stockés : 
- Les logos des associations.
- Les logos présents dans le pied de page du site.
- Les documents de la bibliothèque (modèles à remplir).

Tandis que dans le bucket privé sont stockés les documents déposés dans le cadre d'une inscription, d'un dépôt de charte ou d'un dépôt de projet (tous sont chiffrés).

Il est recommandé d'utiliser le [client AWS](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) en créant un profil de connexion pour gérer le compte utilisé.
```sh
aws configure --profile PROFILE_NAME # utilitaire pour créer un nouveau profil (spécifier Access et Secret Keys)
```

Un bucket distinct doit ensuite être créé par environnement de déploiement et par paramétrage (un public et un privé).
```sh
aws s3api create-bucket --bucket AWS_STORAGE_PRIVATE_BUCKET_NAME --endpoint-url AWS_S3_ENDPOINT_URL --profile PROFILE_NAME
```

Pour le bucket public, il faut penser à ajouter une policy dédiée pour que les fichiers uploadés héritent des caractéristiques publiques du bucket :
```sh
aws s3api create-bucket --bucket AWS_STORAGE_PUBLIC_BUCKET_NAME --endpoint-url AWS_S3_ENDPOINT_URL --profile PROFILE_NAME --policy file://policy.json
```

Où le fichier `policy.json` contiendrait ceci :
```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"PublicRead",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::AWS_STORAGE_PUBLIC_BUCKET_NAME/*"]
    }
  ]
}
```

### Ressources statiques (fichiers PDF)

Les templates PDF (et leurs fichiers statiques liés) utilisés pour la génération d'exports et de notifications (voir partie "Personnalisation / Exports et notifications PDF") sont stockés dans le même bucket.

Les templates PDF sont ceux utilisés par Django, ils utilisent donc Jinja2 et des templatetags. Des modèles d'exemples sont mis à disposition dans le dossier `templates/pdf/**/*.html`.

Si S3 est activé, les modèles stockés localement ne sont plus utilisés.

Dans les fichiers HTML, il est nécessaire de modifier les champs `{% load static %}` en `{% load plana_tags %}` et les appels à `{% static CHEMIN_DU_FICHIER %}` par `{% s3static CHEMIN_DU_FICHIER %}` (penser également à changer les chemins des fichiers pour refléter les routes utilisées sur S3).
