# Compte rendu - TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Nom :** ESSIFI Aymene · **Groupe :** G2 · **Date :** 23/11/2026

> Les sorties et mesures Docker ci-dessous ont été relevées dans l'environnement de travail.

## 1. Mise en place

Résultat constaté après démarrage de Docker Desktop :

```text
docker run --rm hello-world : Hello from Docker!
docker version :
  Client 29.8.2, API 1.56, Windows/amd64, contexte desktop-linux
  Server Docker Desktop 4.95.0 (242831), Engine 29.8.2, Linux/amd64
```

La suite `python -m pytest -q` après correction est consignée à la fin du sprint 2.

## 2. Image et conteneur

1. Une image est le modèle immuable construit à partir du Dockerfile; un conteneur est une
   instance en cours d'exécution de cette image, avec son processus et sa configuration.
2. Les dépendances changent moins souvent que le code. En copiant le fichier de dépendances
   d'abord, Docker peut réutiliser la couche `pip install` si seuls les fichiers de code changent.
3. Le modèle sérialisé doit être chargé avec la version de scikit-learn utilisée pour le créer.
   Une version exacte (`==1.8.0`) évite qu'un build installe une version différente de façon imprévisible.
4. MLflow et DVC servent au suivi d'entraînement et au versionnement des données, pas au service
   de prédiction. Pytest est un outil de développement; aucun n'est nécessaire pour l'API/UI en production.

## 3. Sprint 1 : Dockerfile

```dockerfile
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
```

| Build | Durée | Taille de l'image |
|---|---|---|
| Premier build | Environ 8 min 55 s (BuildKit : 314,6 s pour installer les dépendances, 217,9 s pour exporter l'image; durée totale non chronométrée séparément) | 1,13 GB |
| Après modification du docstring de `maintai/predict.py` | 11,33 s | 1,13 GB |

`CACHED` indique que Docker a réutilisé une couche déjà construite, car ses entrées n'ont pas
changé. Au second build, `WORKDIR`, `COPY requirements-docker.txt` et `RUN pip install` étaient
`CACHED`; les `COPY` du code/UI ont été recalculés après la modification de `predict.py`.

## 4. Sprint 1 : lancer un conteneur

Préparer les données, le modèle et le fichier de clé depuis PowerShell :

```powershell
python -m maintai.dataset
python -m maintai.train
Copy-Item .env.example .env
# Modifier MAINTAI_API_KEY dans .env avant de continuer.
docker build -t maintai:0.4.0 .
docker run -d --name maintai-api -p 127.0.0.1:8000:8000 --env-file .env --mount "type=bind,source=$((Resolve-Path .\models).Path),target=/app/models,readonly" maintai:0.4.0
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 2
  curl.exe --noproxy '*' -sS --max-time 2 http://127.0.0.1:8000/health > $null
  if ($LASTEXITCODE -eq 0) { $ready = $true; break }
}
if (-not $ready) { docker logs maintai-api; throw 'L’API ne répond pas sur le port 8000.' }
```

Requêtes à lancer après démarrage (remplacer la clé d'exemple par la valeur choisie dans `.env`) :

```powershell
$apiKey = ((Get-Content .env | Where-Object { $_ -like 'MAINTAI_API_KEY=*' }) -split '=', 2)[1]
curl.exe --noproxy '*' -i http://127.0.0.1:8000/health
curl.exe --noproxy '*' -i -X POST -H 'Content-Type: application/json' --data-binary '@releve.json' http://127.0.0.1:8000/v1/predict
curl.exe --noproxy '*' -i -X POST -H 'Content-Type: application/json' -H "X-API-Key: $apiKey" --data-binary '@releve.json' http://127.0.0.1:8000/v1/predict
```

Résultats réellement observés :

| Essai | Réponse |
|---|---|
| `GET /health` avec modèle monté | HTTP 200, `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | HTTP 401, `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict` avec la clé correcte | HTTP 200, `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-23T10:33:37Z"}` |

**Piège 1.** Testé sans montage du modèle : `/health` répond HTTP 200 avec `model_loaded:false`.
Une prédiction sans clé répond HTTP 401; avec la clé valide, elle répond HTTP 503
(`Modèle non chargé`) car le modèle n'est pas présent dans l'image.

**Piège 2.** Testé en lançant Uvicorn avec `--host 127.0.0.1` et en publiant le port 8002 :
`docker logs test` indique `Uvicorn running on http://127.0.0.1:8000`, mais la requête du PC
vers `http://localhost:8002/health` échoue (curl HTTP 000 / réponse vide). Le serveur écoute
uniquement sur la boucle locale du conteneur; il faut `--host 0.0.0.0`.

Commande ayant servi à vérifier le piège :

```powershell
docker run -d --name test -p 127.0.0.1:8002:8000 --env-file .env --mount "type=bind,source=$((Resolve-Path .\models).Path),target=/app/models,readonly" maintai:0.4.0 uvicorn maintai.api.main:app --host 127.0.0.1 --port 8000
docker logs test
curl.exe -4 --noproxy '*' -i http://localhost:8002/health
docker rm -f test
```

## 5. Sprint 2 : Docker Compose

```yaml
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command:
      - python
      - -m
      - streamlit
      - run
      - ui/app.py
      - --server.address=0.0.0.0
      - --server.port=8501
      - --server.headless=true
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "127.0.0.1:8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

Commandes de lancement et d'arrêt :

```powershell
docker compose up -d --build
docker compose ps
```

Le lancement final a été effectué avec `docker compose up -d --no-build`, car l'image vérifiée
était déjà construite. Les deux services ont été laissés en marche.

Sortie observée de `docker compose ps` :

```text
tp6-api-1   maintai:0.4.0   Up   127.0.0.1:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   Up   127.0.0.1:8501->8501/tcp
```

La barre latérale affiche `http://api:8000`, valeur de `MAINTAI_API_URL` définie dans le service
`ui`; cette valeur a été vérifiée dans l'environnement du conteneur. Compose résout `api` comme
nom DNS du service sur son réseau interne. La page Streamlit `http://localhost:8501/` répond HTTP 200.

Affichage observé dans le navigateur (`http://localhost:8501/`) :

- Titre : `MaintAI · prédiction de panne`; URL API préremplie : `http://api:8000`.
- Onglet « Données » : 5 000 relevés, 13,6 % de pannes, température moyenne de 59,8 °C.
- Graphique du taux de panne selon la température (10 tranches) et nuage de points température/vibration
  sur 500 relevés.
- Onglet « Prédiction » : formulaire visible, valeurs initiales 72 °C, 6 mm/s, 85 % de charge et
  15 000 heures; le champ de clé API est masqué.
- La console du navigateur signale un avertissement Vega non bloquant sur l'échelle du graphique;
  le contenu s'affiche correctement et la page répond HTTP 200.

Résultat des deux contrôles exécutés depuis `ui` :

```powershell
docker compose exec -T ui python -c "import httpx; print(httpx.get('http://api:8000/health').json())"
{'status': 'ok', 'model_loaded': True}

docker compose exec -T ui python -c "import socket; s=socket.socket(); s.settimeout(3); print(s.connect_ex(('127.0.0.1',8000))); s.close()"
111
```

`api` fonctionne par le DNS Compose. `localhost` désigne le conteneur UI lui-même; le code 111
signifie que rien n'écoute sur son port 8000.

Arrêter et supprimer les conteneurs et le réseau du projet :

```powershell
docker compose down
```

Dernière ligne de `python -m pytest -q` après correction :

```text
38 passed, 2 warnings in 161.18s
```

Les avertissements proviennent de MLflow sur les colonnes entières du schéma; les tests passent.

## 6. Décision : ADR 005

Le Dockerfile construit une image contenant le code et les dépendances figées, mais pas les données,
le modèle ni les secrets. Au lancement, les données et le modèle sont montés en lecture seule et
la clé API est injectée via `.env`, ce qui garde l'image réutilisable et évite d'y intégrer des secrets.

## 7. Questions de compréhension

1. Le code et les dépendances entrent dans l'image avec `COPY` et `pip install`. Le modèle et les
   données arrivent au lancement par volumes; la clé arrive par variable d'environnement via `--env-file`.
2. Une clé inscrite dans une image pourrait être extraite et serait conservée dans ses couches et
   son historique. Elle est injectée au démarrage et le fichier `.env` est exclu du contexte Docker.
3. Docker ajoute la nécessité de livrer ou monter le modèle entraîné, de conserver la compatibilité
   de version des bibliothèques et de configurer le chemin du modèle dans le conteneur.

## 8. Le rendu Git

- Lien de pull request : non créé dans cette session.
- Tag `tp6` sur GitHub : non créé/vérifié.
- Aucun commit n'a été créé. Le fichier `.gitignore` exclut `.env`, `models/` et `data/*.csv`,
  conformément à la consigne de ne pas versionner secrets, modèle ou données. Le statut Git global
  n'est pas indiqué car la racine Git détectée est le dossier personnel, qui contient des modifications
  sans rapport avec le TP.

## 9. État final

- L'application est lancée localement : interface `http://localhost:8501`, API `http://localhost:8000`.
- Le `.env` créé localement contient une clé générée pour ce TP; il est ignoré par Git et ne doit pas
  être partagé ni utilisé en production.
- Aucun commit, tag `tp6` ou pull request n'a été créé; à effectuer seulement si la remise du cours l'exige.
