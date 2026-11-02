# Choix des Modèles — Projet MaintAI & CantineAI

**Date :** 26/10/2026 · **Auteur / Groupe :** ESSIFI AYMENE

---

## 1. Modèle MaintAI (Prédiction des pannes de machines)

### Contexte
MaintAI vise à prédire les pannes de machines à partir de relevés de capteurs afin d'aider le responsable de maintenance à planifier les inspections. Une panne manquée pouvant entraîner l'arrêt d'une ligne de production pendant une journée, la métrique principale retenue est le **recall**, qui mesure la proportion de pannes réelles détectées par le modèle.

### Données et découpage
- **Fichier :** `data/exemple_pannes.csv`
- **Nombre de lignes :** 5 000 relevés synthétiques.
- **Variables utilisées :** température, vibration, charge et heures de fonctionnement.
- **Variable cible :** `failure` (proportion de pannes : 17,6 %).
- **Découpage :** Stratifié / Aléatoire sur jeu d'entraînement et jeu de test.

### Résultats sur le jeu de test

| Modèle | Recall (métrique principale) | Accuracy | Precision | F1-score |
|---|---:|---:|---:|---:|
| Baseline | 0,000 | 0,824 | 0,000 | 0,000 |
| **Régression logistique** | **0,847** | **0,839** | **0,527** | **0,649** |
| Forêt aléatoire | 0,540 | 0,882 | 0,720 | 0,617 |
| Gradient Boosting | 0,608 | 0,888 | 0,713 | 0,656 |
| K plus proches voisins (KNN) | 0,540 | 0,878 | 0,699 | 0,609 |

### Décision & Limites
Le modèle retenu est la **Régression logistique** (Recall de **0,847**). 
- **Point fort :** Détecte 84,7 % des pannes réelles, atteignant le critère d'acceptation de Recall $\ge 0,80$.
- **Limites :** La précision est de 0,527, signifiant qu'environ 47,3 % des alertes sont de fausses alertes générant des inspections inutiles.

---

## 2. Modèle CantineAI (Prévision des repas de cantine)

### Contexte
CantineAI prédit le nombre de repas à préparer pour le lendemain dans une cantine scolaire à partir des informations disponibles au moment de la commande. La métrique principale est la **MAE** (erreur absolue moyenne), car elle indique directement le nombre moyen de repas d'écart entre les prévisions et les valeurs réelles.

### Données et découpage
- **Fichier :** `data/cantine_repas.csv`
- **Nombre de lignes :** 340 jours d'école synthétiques.
- **Cible :** `repas_servis`.
- **Variables utilisées :** `date`, `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_semaine_precedente`.
- **Découpage :** Chronologique (80 % entraînement / 20 % test, soit 272 / 68 lignes).

### Résultats sur le jeu de test

| Modèle | MAE (métrique principale) | RMSE | $R^2$ |
|---|---:|---:|---:|
| Baseline | 70,271 | 88,416 | -0,151 |
| **Régression Ridge** | **22,623** | **28,545** | **0,880** |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Random Forest | 31,845 | 41,540 | 0,746 |
| K plus proches voisins (KNN) | 36,212 | 46,037 | 0,688 |

### Décision & Limites
Le modèle retenu est la **Régression Ridge** (MAE de **22,623 repas**).
- **Point fort :** Réduction de 67,8 % de l'erreur par rapport à la baseline (MAE ≤ 25, RMSE ≤ 35, $R^2 \ge 0,80$ respectés).
- **Limites :** Le jeu de test comporte 68 lignes synthétiques et le traitement des valeurs manquantes (`repas_semaine_precedente`) demande une attention continue post-vacances.