"""Configuration du projet.

Le projet est paramétré pour le prototype CantineAI : prédire le nombre de repas
servis le lendemain à partir des données de la cantine et d'un découpage
chronologique. Le cas MaintAI est aussi documenté ci-dessous pour faciliter le
basculement entre les deux prototypes du cahier de charges.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROTOTYPE = "cantine"

if PROTOTYPE == "maintai":
    DATA_PATH = ROOT / "data" / "exemple_pannes.csv"
    TARGET = "failure"
    TASK = "classification"
    MAIN_METRIC = "recall"
    SPLIT = "random"
    TIME_COLUMN = None
else:
    DATA_PATH = ROOT / "data" / "cantine_repas.csv"
    TARGET = "repas_servis"
    TASK = "regression"
    MAIN_METRIC = "mae"
    SPLIT = "chronologique"
    TIME_COLUMN = "date"

FEATURES = None  # None = toutes les colonnes sauf la cible ; sinon une liste de noms
TEXT_COLUMN = None  # colonne de texte libre, sinon None

TEST_SIZE = 0.2
SEED = 42
MODELS_DIR = ROOT / "models"
