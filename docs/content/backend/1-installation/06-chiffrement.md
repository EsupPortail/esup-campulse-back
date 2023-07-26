---
title: Chiffrement
weight: 106
---

L'application utilise deux types de chiffrements pour sécuriser les échanges et le stockage de documents. Il est nécessaire de générer des clés publiques et privées dans le dossier `keys` via les commandes suivantes :
- `$ python manage.py generate_jwt_keys` pour générer les clés JWT SHA256 nécessaires à l'authentification des comptes.
- `$ python manage.py generate_age_keys` pour générer les clés AGE nécessaires au chiffrement des documents stockés par les étudiantes et étudiants.

Si le package `age` ne peut être installé sur la machine cible, générer les clés sur une autre machine et les envoyer sur la machine cible manuellement :
```sh
$ python manage.py generate_age_keys
$ scp -r keys/age-private-key.key USER@DOMAIN.TLD:/APP_FOLDER/keys/
$ scp -r keys/age-public-key.key USER@DOMAIN.TLD:/APP_FOLDER/keys/
```
