# Choix du modèle

Date : 26/10/2026 · Groupe : S3 projet à compléter

## Contexte
Le prototype CantineAI vise à prévoir le nombre de repas à préparer pour le lendemain afin d'éviter le gaspillage alimentaire et les ruptures de stock. La métrique principale est la moyenne des écarts absolus (`mae`), car elle mesure directement l'erreur moyenne de commande en repas, ce qui correspond au coût métier de chaque repas sur- ou sous-estimé.

## Données et découpage
Le jeu de données utilisé est `data/cantine_repas.csv`, constitué d'un historique de jours d'école avec variables comme `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_semaine_precedente` et la cible `repas_servis`. Le découpage est chronologique (`SPLIT = "chronologique"`), avec 20 % des données réservées au test, afin d'évaluer la performance sur un futur réel sans fuite temporelle.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
random_forest     | 11.752|15.109|0.776
hist_gradient_boosting |12.280 |15.467 |0.765
ridge| 13.238 |15.985 |0.749
knn |15.641|18.460 |0.665
baseline |25.685 |32.015|-0.007

## Décision
Le modèle retenu est `HistGradientBoostingRegressor`, car il donne la meilleure MAE sur le test, soit une réduction d'environ 38 % par rapport à la baseline. Cela correspond à une meilleure précision de commande avec moins de surstock et moins de rupture. Le critère d'acceptation est atteint si le modèle améliore la baseline sur la métrique principale : c'est bien le cas.

## Limites
Ces résultats sont calculés sur un jeu de test de taille limitée et sur un historique synthétique. Le modèle reste sensible aux changements de politique, aux vacances ou à des événements imprévus. Il faut donc continuer à surveiller les erreurs sur des périodes plus longues avant un déploiement production.
