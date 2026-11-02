# Étude de Conception Globale — MaintAI & CantineAI

**Version :** 1.0 · **Date :** 26/10/2026 · **Auteur :** ESSIFI AYMENE

---

# Part 1 — Prototype MaintAI (Maintenance Prédictive)

## 1. Contexte, Problème & Utilisateurs
- **Utilisateur principal :** Responsable / Équipe de maintenance d'une usine.
- **Besoin :** Prioriser chaque matin les machines à inspecter toutes les 5 minutes pour éviter des interruptions de chaîne de production.
- **Coûts des erreurs :**
  - **Faux Négatif (Panne manquée) :** Arrêt complet d'une ligne de production pendant une journée (Coût très élevé).
  - **Faux Positif (Fausse alerte) :** ~1 heure d'inspection inutile d'une machine.

## 2. Données & Approche

| Paramètre | Description |
|---|---|
| **Source & Volume** | `data/exemple_pannes.csv` — 5 000 relevés synthétiques |
| **Variables d'entrée** | Température, vibration, charge, heures de fonctionnement |
| **Variable cible** | `failure` (0 ou 1, avec 17,6 % de pannes réelles) |
| **Type de problème** | Classification binaire supervisée |

## 3. Métriques et Critères d'Acceptation

- **Métrique prioritaire :** Recall / Rappel ($\ge 0,85$ souhaité en cible de conception, $\ge 0,80$ sur test).
- **Métriques complémentaires :** Precision ($\ge 0,60$), F1-score ($\ge 0,70$), Accuracy.
- **Baseline :** `DummyClassifier` (most frequent) — Recall = 0,000, Accuracy = 0,824.

---

# Part 2 — Prototype CantineAI (Prévision des Repas)

## 1. Contexte, Problème & Utilisateurs
- **Utilisateur principal :** Gestionnaire de la cantine scolaire.
- **Besoin :** Estimer chaque jour avant 10 h le nombre précis de repas à commander pour le lendemain.
- **Coûts des erreurs :**
  - **Repas en trop (Surestimation) :** Gaspillage alimentaire + ~15 DH de perte par repas.
  - **Repas manquant (Sous-estimation) :** Élèves non servis / Achats d'urgence plus chers.

## 2. Données & Approche

| Paramètre | Description |
|---|---|
| **Source & Volume** | `data/cantine_repas.csv` — 340 jours d'école synthétiques |
| **Variables d'entrée** | Date, jour, inscrits, menu, température, pluie, examens, sortie scolaire, veille vacances, repas semaine précédente |
| **Variable cible** | `repas_servis` (Nombre de repas) |
| **Type de problème** | Régression sur série temporelle (Découpage chronologique) |

## 3. Métriques et Critères d'Acceptation

- **Métrique prioritaire :** MAE ($\le 25$ repas).
- **Métriques complémentaires :** RMSE ($\le 35$ repas), $R^2$ ($\ge 0,80$).
- **Baseline :** Historique simple du même jour de la semaine précédente (MAE = 70,271 repas).

---

# Part 3 — Synthèse Comparative des Deux Prototypes

| Élément | MaintAI | CantineAI |
|---|---|---|
| **Objectif** | Prédire si une machine tombera en panne | Prévoir le nombre de repas à servir |
| **Type de problème** | Classification binaire | Régression temporelle |
| **Variable Cible** | `failure` (0 ou 1) | `repas_servis` (Entier) |
| **Données** | 5 000 relevés de capteurs | 340 jours d'école |
| **Risque principal** | Panne manquée (Arrêt usine) | Gaspillage ou manque de nourriture |
| **Métrique prioritaire** | Recall / Rappel | MAE (Erreur absolue moyenne) |
| **Validation** | Découpage stratifié / indépendant | Découpage chronologique (80/20) |
| **Prise de décision** | Priorisation des inspections par les techniciens | Ajustement final du bon de commande par le gestionnaire |