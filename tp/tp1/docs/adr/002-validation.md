# ADR 002 : validation des relevés et disponibilité du modèle

Date : 26/10/2026 · Auteurs : Aymene ESSIFI, Mouna LANOUARI et Rihab ZIDANI

## Contexte

L’API reçoit des mesures de capteurs qui doivent respecter des limites physiques
avant d’être transmises au modèle. Le modèle peut également être absent au
démarrage, par exemple avant le premier entraînement ou après un déploiement
incomplet.

## Options étudiées

1. Accepter des valeurs sans limites métier : simple, mais des mesures
   impossibles ou incohérentes atteindraient le modèle.
2. Valider les mesures à l’entrée avec Pydantic : les limites sont vérifiées
   avant la prédiction et documentées automatiquement dans OpenAPI.
3. Arrêter le serveur si le modèle manque : rend le problème visible
   immédiatement, mais empêche aussi l’API et son endpoint de santé de démarrer.
4. Démarrer sans modèle et répondre `503 Service Unavailable` aux prédictions :
   l’API reste joignable et signale explicitement que le service de prédiction
   n’est pas prêt.

## Décision

Utiliser un schéma Pydantic avec des plages réalistes : température de −40 à
150 °C, vibration de 0 à 100 mm/s, charge de 0 à 100 % et durée de
fonctionnement de 0 à 200 000 heures (environ 23 ans de fonctionnement continu).
Ces limites décrivent des valeurs physiques et une plage de mesure opérationnelle,
et non les extrêmes observés dans le jeu de données synthétique.

Si le modèle est absent, laisser démarrer l’API et renvoyer `503` uniquement sur
`POST /v1/predict`. Le message d’erreur indique qu’il faut entraîner le modèle.
`GET /health` reste disponible et son champ `model_loaded` signale l’absence du
modèle.

## Conséquences

Les entrées invalides sont rejetées par FastAPI avec le statut `422`, avant
l’appel au modèle, et les bornes sont visibles dans `/docs`. Les appels de
prédiction ne provoquent pas une erreur serveur `500` lorsque l’artefact manque.
En contrepartie, les clients doivent traiter `503` et réessayer après le
déploiement du modèle. L’API reste démarrée : une supervision de disponibilité
doit donc tenir compte de `model_loaded`, pas seulement du statut HTTP de
`/health`.
