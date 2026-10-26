# Étude de conception — CantineAI

Groupe : S3 projet à compléter · Version : finale · Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal : le gestionnaire de la cantine d'un lycée.

## 2. Problème et décision
- Décision prise avec le système : commander le nombre de repas du lendemain en fonction du menu, de la météo, du nombre d'élèves inscrits et du calendrier.
- Fréquence : chaque jour à 10 h pour la commande du lendemain.
- Coût d'une erreur : un repas en trop génère du gaspillage alimentaire (matière première perdue) ; un repas manquant perturbe la restauration et oblige à acheter des sandwichs de remplacement ou crée des plaintes parentales.

## 3. Approche par sous-problème
| Sous-problème | Approche | Pourquoi pas une approche plus simple |
|---|---|---|
| Prévision du nombre de repas | Modèle de régression supervisée | Une règle manuelle simple est trop peu robuste face à la variabilité de la météo, du menu et des vacances |
| Analyse de saisonnalité | Variables calendaires et historique de la semaine précédente | Une approche purement déterministe ignore les corrélations entre météo, menu et demande réelle |
| Décision de commande | Modèle ML comparé à une baseline | La baseline est utile comme point de référence, mais ne capture pas les interactions entre les variables |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/cantine_repas.csv` | Données synthétiques du cours, sans licence spécifique | ~340 jours d'école | Non |

## 5. Métriques, baseline et critères d'acceptation
- Baseline : modèle naïf qui prédit la moyenne du nombre de repas servis sur les jours passés.
- Métrique principale : `mae` (mean absolute error), car elle mesure directement l'erreur moyenne de commande en repas, ce qui est proche du coût métier.
- Critère d'acceptation : sur le jeu de test chronologique, le modèle retenu doit améliorer la baseline sur la MAE, et idéalement rester sous une erreur moyenne de 30 repas par jour.

## 6. Architecture prévue
- Chargement des données ;
- découpage chronologique ;
- préparation des attributs numériques et catégoriels ;
- entraînement de plusieurs modèles ;
- évaluation sur le test ;
- sauvegarde du meilleur modèle et des métriques.

## 7. Choix technologiques
- Python, pandas, scikit-learn ;
- pipeline de preprocessing avec imputations et encodage catégoriel ;
- comparatif de modèles de régression : baseline, Ridge, RandomForest, HistGradientBoosting, KNN.

## 8. Risques, éthique, confidentialité
- Risque de sur- ou sous-estimation, surtout lors d'événements imprévus ;
- données synthétiques, donc aucun risque réel de confidentialité ;
- besoin de surveiller le système et de recalibrer les prédictions sur des périodes plus longues.

## 9. Limites et hors périmètre
- Le projet couvre la prévision pour la cantine et non la gestion complète des achats ;
- les modèles sont entraînés sur un historique synthétique ;
- le cahier de charges ne couvre pas l'intégration métier, l'API web ni le tableau de bord de commande.
