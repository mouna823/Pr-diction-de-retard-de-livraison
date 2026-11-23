# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :
Hello from Docker!
This message shows that your installation appears to be working correctly

Client:
 Version:           29.9.3
 API version:       1.56
 Go version:        go1.26.10
 Git commit:        5457199
 Built:             Tue Nov  3 21:46:10 2026
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.99.0 (245822)
 Engine:
  Version:          29.9.3
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.10
  Git commit:       70efc0e
  Built:            Tue Nov  3 21:41:42 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.4.2
  GitCommit:        b7a25261e029d68978bbf290df0a62fc819b3c51
 runc:
  Version:          1.5.2
  GitCommit:        v1.5.2-0-g29dd3dc2
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0

Dernière ligne de `python -m pytest` après la mise en place :

```
(collez ici)
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   …
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   …
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   …
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   …

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

FROM python:3.11-slim
WORKDIR /app
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt
COPY maintai ./maintai
COPY ui ./ui
ENV MAINTAI_MODELS_DIR=/app/models \
    MAINTAI_DATA_PATH=/app/data/sensors.csv
EXPOSE 8000
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build |203,9 s|1,13GB |
| après une modification de `maintai/predict.py` |5.6s |1,13GB |

Que signifie `CACHED` dans le journal du second build ?

les étapes marquées CACHED sont des couches réutilisées.

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

ls:ro" maintai:0.4.0
9277ad06eda012840590eb8b2f1c1efa57f1d39fcb8cf51c8973fdac3b16c44d

| Essai | Réponse |
|---|---|
| `GET /health` |true |
| `POST /v1/predict` sans clé |Clé API absente ou invalide |
| `POST /v1/predict` avec la clé |"failure_probability": 0,"alert": true, |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

{"status":"ok","model_loaded":false}

{"detail":"Clé API absente ou invalide"}

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?
 docker logs test
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
(.venv) PS C:\Users\LENOVO\Downloads\S8-tp6\TP6> curl.exe http://localhost:8002/health
curl: (52) Empty reply from server

docker logs test montre qu'uvicorn tourne sur 127.0.0.1:8000, mais http://localhost:8002/health ne répond pas (« Empty reply from server »). Dans un conteneur, 127.0.0.1 ne désigne que le conteneur lui-même. Les requêtes redirigées par -p arrivent par son interface réseau, donc uvicorn ne les reçoit pas. Il faut écouter sur 0.0.0.0.


## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
(collez ici)
```

Sortie de `docker compose ps` :

```
(collez ici)
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

…

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
(collez ici)
```

…

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
(collez ici)
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

…

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   …
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   …
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   …

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp6` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? oui / non

## 9. Ce qui reste flou

…
