
# CantineAI — projet de prévision des repas

Ce projet répond au cahier de charges du prototype CantineAI : prédire le nombre de repas à commander pour le lendemain à partir des données historiques de la cantine, du menu, de la météo et du calendrier scolaire.

## Objectif

- prédire la colonne `repas_servis` ;
- optimiser une régression sur série temporelle ;
- comparer plusieurs modèles avec une métrique principale orientée coût métier ;
- sauvegarder le meilleur modèle dans `models/model.joblib`.

## Données

Le jeu de données est dans `data/cantine_repas.csv`.

Colonnes principales :
- `date`
- `jour`
- `inscrits`
- `menu`
- `temperature_c`
- `pluie_mm`
- `examens`
- `sortie_scolaire`
- `veille_vacances`
- `repas_semaine_precedente`
- `repas_servis`

## Configuration

La configuration par défaut est alignée avec le cahier de charges :
- `TARGET = "repas_servis"`
- `TASK = "regression"`
- `MAIN_METRIC = "mae"`
- `SPLIT = "chronologique"`
- `TIME_COLUMN = "date"`

Le prototype `maintai` reste disponible en changeant `PROTOTYPE = "maintai"` dans `monprojet/config.py`.

## Exécution

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
python -m monprojet.train
```

Le script d'entraînement affiche une comparaison des modèles et sauvegarde les artefacts dans `models/`.
