# ADR 005 : séparer l'image Docker des données, du modèle et des secrets

Date : 23/11/2026 · Auteur : ESSIFI Aymene · Groupe : G2

## Contexte

MaintAI doit pouvoir servir des prédictions dans un conteneur sans incorporer les données et le
modèle propres à une exécution. La clé API est un secret et ne doit pas être publiée dans une image.

## Options étudiées

1. Copier code, modèle, données et configuration dans une seule image : déploiement simple,
   mais image liée aux données et risque d'exposer ou de figer des secrets.
2. Construire une image avec le code et les dépendances, puis monter les données/le modèle et
   injecter les secrets à l'exécution : responsabilités séparées, avec les fichiers à fournir au lancement.

## Décision

Retenir l'option 2. L'image contient le code et des dépendances figées; les dossiers `models/` et
`data/` sont montés en lecture seule et `.env` transmet la clé API au démarrage.

## Conséquences

La même image peut être réutilisée avec différents modèles/configurations sans rebuild, et les secrets
ne sont pas intégrés à ses couches. Le déploiement doit fournir les dossiers attendus et protéger
le fichier `.env`; la version de scikit-learn reste figée pour assurer la compatibilité du modèle.
