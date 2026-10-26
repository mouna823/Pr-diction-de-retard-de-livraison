# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G2 · **Membres :** Aymene ESSIFI, Mouna LANOUARI et Rihabe ZIDANI · **Date :** 26/10/2026

> Les sorties ci-dessous proviennent des exécutions locales du TP. Les informations
> liées au dépôt GitHub (pull request, tag et relecture) restent à renseigner après
> la publication du projet sur le dépôt de votre groupe.

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place :

```text
======================== 3 failed, 10 passed in 11.46s ========================
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà :

- `test_health`
- `test_out_of_range_value_is_rejected`
- `test_missing_field_is_rejected`
- `test_openapi_documents_predict`

Les deux tests de validation (`test_out_of_range_value_is_rejected` et
`test_missing_field_is_rejected`) passent pour une mauvaise raison. Au départ,
`SensorReading` ne déclare aucun champ et `extra="forbid"` interdit donc chacun
des champs envoyés. FastAPI renvoie `422` pour les deux requêtes, sans vérifier
correctement la borne de température ni identifier le champ manquant. Le test
qui vérifie uniquement le statut donne alors un faux sentiment de sécurité.

Les trois tests API en échec sont ceux de la prédiction normale, de l'alerte et
du modèle manquant : l'endpoint n'est pas encore implémenté à cette étape.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique |
|---|---:|---:|---:|---|
| `temperature_c` | `float` | -40 °C | 150 °C | Plage de mesure moteur étendue aux conditions froides et aux températures élevées ; limites données dans le polycopié. |
| `vibration_mm_s` | `float` | 0 mm/s | 100 mm/s | Une vitesse vibratoire ne peut pas être négative ; la limite supérieure couvre la plage d'un capteur industriel, y compris des vibrations anormalement fortes. |
| `load_pct` | `float` | 0 % | 100 % | Une charge est exprimée comme une fraction de la capacité nominale : de l'arrêt à la pleine charge. |
| `runtime_hours` | `float` | 0 h | 200 000 h | Le compteur ne peut pas être négatif ; 200 000 h représentent environ 22,8 ans de fonctionnement continu et couvrent une longue durée de vie industrielle. |

Ces bornes représentent des limites physiques ou opérationnelles, et ne sont pas
calquées sur les valeurs minimales et maximales du jeu de données synthétique.
Les champs restent des `float`, notamment pour accepter des mesures fractionnaires.

Après avoir écrit `schemas.py` seul, `python -m pytest` donne :

```text
======================== 3 failed, 10 passed in 7.16s =========================
```

Les trois échecs sont `test_predict_returns_probability`,
`test_high_risk_reading_raises_alert` et `test_503_when_model_missing`. Ils
atteignent désormais la fonction `predict()` et échouent avec
`NotImplementedError`. C'est un bon signe : le schéma accepte les relevés
valides et les transmet à l'endpoint ; les bornes invalident bien les entrées
hors plage.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Corps de la fonction :

```python
predictor: Predictor | None = state.get("predictor")
if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle indisponible. Entraînez le modèle avant de demander une prédiction.",
    )

return PredictionOut(**predictor.predict(reading.model_dump()))
```

On répond **503 Service Unavailable** plutôt que 500 car l'API fonctionne, mais
le service de prédiction ne peut temporairement pas être rendu : l'artefact du
modèle n'est pas disponible. Le statut indique au client la nature du problème
et qu'un nouvel essai pourra réussir après l'entraînement ou le déploiement du
modèle. Le code 500 signalerait plutôt une erreur inattendue du serveur.

Le modèle est chargé une fois au démarrage, dans `lifespan`, pour éviter de
relire les fichiers du modèle à chaque requête et d'ajouter ce coût à chaque
prédiction. Toutes les requêtes réutilisent ainsi le même modèle en mémoire.

## 4. Les tests

Dernière ligne de `python -m pytest` après l'implémentation :

```text
============================= 13 passed in 5.35s ==============================
```

## 5. L'API en marche

Requêtes envoyées à l'application après génération des données et entraînement
du modèle :

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-26T10:52:10Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

Quand le modèle manque, `POST /v1/predict` renvoie `503` avec le détail :
`{"detail":"Modèle indisponible. Entraînez le modèle avant de demander une prédiction."}`.

Dans `/docs`, ouvrir `POST /v1/predict`, puis le schéma du corps de requête
`SensorReading` : chaque champ y affiche son type, ses bornes et sa description.
L'exemple de relevé se trouve également dans ce schéma.

## 6. Questions de compréhension

1. **REST et FastAPI : quelle est la différence ?** REST est un ensemble de
   principes pour structurer une API web (ressources, routes, méthodes HTTP,
   statuts et représentation des données). FastAPI est une bibliothèque Python
   qui permet de construire une API respectant ces principes.
2. **Le schéma Pydantic sert à trois choses. Lesquelles ?** Il valide les
   données entrantes, fournit à FastAPI les informations pour générer la
   documentation OpenAPI et `/docs`, et convertit la requête en objet Python
   typé utilisable par la fonction.
3. **Dans `http://localhost:8000/v1/predict`, que désignent `localhost`,
   `8000` et `/v1/predict` ?** `localhost` est la machine locale ; `8000` est
   le port d'écoute du serveur ; `/v1/predict` est la route/version de l'API.
4. **Pourquoi `/v1` dans l'adresse ?** La version permet de faire évoluer le
   contrat de l'API sans casser les clients qui utilisent encore une ancienne
   version.
5. **Dans `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et
   `app` ?** `maintai.api.main` est le chemin Python vers le module
   `maintai/api/main.py` ; `app` est la variable de ce module contenant
   l'application FastAPI à exécuter.

## 7. Le rendu Git

- **Lien de la pull request :** à renseigner après publication sur GitHub.
- **Le tag `tp1` existe sur GitHub :** non vérifiable depuis ce dossier local ;
  à créer après la fusion de la pull request.
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?** à
  renseigner après la relecture par un membre du groupe.

## 8. Ce qui reste à faire

Le code, les tests et la documentation technique du TP sont préparés. Il reste
à renseigner le groupe et les membres, puis à pousser les fichiers sur le dépôt
de l'équipe, ouvrir et faire relire la pull request, la fusionner et créer le
tag `tp1`. Le dossier fourni ici n'est pas configuré avec le dépôt GitHub du
groupe ; ces opérations ne peuvent donc pas être attestées localement.
