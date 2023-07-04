---
title: Serveur
weight: 107
---

L'application a été initialement pensée pour être déployée avec [Fabric](https://www.fabfile.org/) et [Pydiploy](https://pypi.org/project/pydiploy/). Des exemples de configuration sont disponibles dans le dossier `fabfile`.

Le fichier contient également un exemple de Content-Security-Policy pouvant être appliqué (au format Nginx), prenant en compte les ressources chargées par django-admin :

```nginx
add_header Content-Security-Policy "upgrade-insecure-requests; default-src 'none'; base-uri 'self'; connect-src 'self'; font-src 'self' https://stackpath.bootstrapcdn.com; frame-ancestors 'self'; frame-src 'self'; img-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://stackpath.bootstrapcdn.com; style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com;";
```
