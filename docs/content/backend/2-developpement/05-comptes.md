---
title: Comptes de tests
weight: 115
---

Plusieurs comptes de tests sont présents dans le jeu de données initial. Il s'agit de comptes locaux (pas d'identification via CAS), disposant tous d'un mot de passe commun `motdepasse` (excepté pour `compte-non-valide@mail.tld` qui est un compte de test inactif), et de groupes différents.
1. `admin@admin.admin` (permet d'accéder à l'interface d'administration de l'application : `http://localhost:8000/admin/`) : `MANAGER_GENERAL`
2. `compte-non-valide@mail.tld` (nouveau compte avec adresse email non validée) : `STUDENT_INSTITUTION` + `STUDENT_MISC`
3. `gestionnaire-svu@mail.tld` : `MANAGER_GENERAL`
4. `gestionnaire-uha@mail.tld` : `MANAGER_INSTITUTION`
5. `gestionnaire-crous@mail.tld` : `MANAGER_MISC`
6. `membre-fsdie-idex@mail.tld` : `MEMBER_FUND`
7. `membre-culture-actions@mail.tld` : `MEMBER_FUND`
8. `membre-commissions@mail.tld` : `MEMBER_FUND`
9. `etudiant-porteur@mail.tld` : `STUDENT_MISC`
10. `etudiant-asso-hors-site@mail.tld` : `STUDENT_INSTITUTION`
11. `etudiant-asso-site@mail.tld` : `STUDENT_INSTITUTION`
12. `president-asso-hors-site@mail.tld` : `STUDENT_INSTITUTION`
13. `president-asso-site@mail.tld` : `STUDENT_INSTITUTION`
14. `president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld` : `MEMBER_FUND` + `STUDENT_INSTITUTION` + `STUDENT_MISC`
15. `compte-presque-valide@mail.tld` (nouveau compte avec adresse email validée) : `STUDENT_MISC`
16. `gestionnaire-unistra@mail.tld` : `MANAGER_INSTITUTION`
