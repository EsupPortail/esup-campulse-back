---
title: Routes
weight: 111
---

L'application est découpée en plusieurs services accessibles lors du développement :
- [http://localhost:3000/](http://localhost:3000/) : frontend.
- [http://localhost:8000/](http://localhost:8000/) : accès à l'API du backend.
- [http://localhost:8000/admin/](http://localhost:8000/admin/) : interface d'administration Django du backend.
- [http://localhost:1080/](http://localhost:1080/) : serveur de mails MailDev (installer avec `npm install -g maildev`, lancer avec `maildev`).
- [http://localhost:1313/plana/](http://localhost:1313/plana/) : documentation technique générale.
- [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/) : documentation de l'API avec UI Swagger.
- [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/) : documentation de l'API avec UI Redoc.
- [http://localhost:8000/_hc/](http://localhost:8000/_hc/) : page de statut des services du back avec django-health-check.
