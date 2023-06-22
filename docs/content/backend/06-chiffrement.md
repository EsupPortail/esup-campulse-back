---
title: Chiffrement
weight: 106
---

- Exécuter la commande `$ python manage.py generate_jwt_keys` pour générer les clés JWT SHA256 nécessaires à l'authentification des comptes.
- Exécuter la commande `$ python manage.py generate_age_keys` pour générer les clés AGE nécessaires au chiffrement des documents stockés par les étudiantes et étudiants.

Si le package `age` ne peut être installé, générer les clés localement et les envoyer sur le serveur manuellement :
```
$ python manage.py generate_age_keys
$ scp -r keys/age-private-key.key USER@DOMAIN.TLD:/APP_FOLDER/keys/
$ scp -r keys/age-public-key.key USER@DOMAIN.TLD:/APP_FOLDER/keys/
```
