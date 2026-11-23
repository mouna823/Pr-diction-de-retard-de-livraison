# ADR 005 : ce qui entre dans l'image Docker, et ce qui arrive au lancement

Date : 23/11/2026 · Auteurs : [noms du groupe]

## Contexte
MaintAI doit tourner sur un serveur où personne ne prépare de `.venv` : on l'emballe dans une image Docker (`maintai:0.4.0`).
Il faut décider ce que l'image contient : le code et les bibliothèques, mais aussi le modèle, les données, la clé API ?

## Options étudiées

### Décision 1 : où mettre le modèle ?
1. **Modèle dans l'image** (`COPY models ./models`)
   - Gagne : l'image se suffit à elle-même, un seul `docker run` sans volume ; image et modèle sont toujours cohérents.
   - Perd : chaque nouveau modèle oblige à reconstruire et redistribuer l'image ; l'image est plus lourde ; le code et le modèle n'évoluent plus séparément.
2. **Modèle par un volume** (`-v ./models:/app/models:ro`)
   - Gagne : on change de modèle (nouvel entraînement, TP5) sans reconstruire l'image ; l'image reste légère et identique pour tous les modèles ; lecture seule (`:ro`), le conteneur ne peut pas abîmer le modèle.
   - Perd : l'image seule ne suffit pas ; il faut fournir le dossier `models/` au lancement, sinon `/health` répond `model_loaded: false` et `/v1/predict` répond 503.

### Décision 2 : que laisse dehors `.dockerignore` ?
| Exclu | Pourquoi | Si on l'incluait |
|---|---|---|
| `data/`, `models/` | lourds, changent souvent ; ils arrivent par des volumes | image plus lourde, rebuild à chaque nouvelle donnée ou modèle |
| `.env` | contient la clé API, un secret ; une image se partage | n'importe qui ayant l'image lirait la clé |
| `mlflow.db`, `mlruns/`, `.dvc/` | historique d'entraînement et cache local, inutiles pour servir l'API | image plus lourde, rien de gagné à l'exécution |
| `.venv/`, `__pycache__/`, `tests/`, `.git/` | propres à un PC, ou inutiles en production | fichiers Windows inutilisables sous Linux, image plus lourde |

## Décision
- Le modèle arrive **par un volume en lecture seule**, et pas dans l'image : un nouveau modèle ne doit pas exiger un nouveau build.
- L'image contient **seulement le code (`maintai/`, `ui/`) et les bibliothèques figées** (`requirements-docker.txt`). Les données et le modèle arrivent par des volumes, la clé par `--env-file .env` (ou `env_file` dans Compose).

## Conséquences
- Facilite : mettre à jour le modèle sans toucher à l'image ; partager l'image sans exposer de secret ; des builds rapides grâce au cache.
- Rend plus difficile : le lancement demande toujours le volume `models/` et le fichier `.env`, d'où l'intérêt de `compose.yaml`.
- À surveiller : le modèle monté doit avoir été écrit avec la même version de scikit-learn que l'image (`scikit-learn==1.8.0`) ; le dossier `models/` doit exister avant `docker run` (`python -m maintai.train`).
