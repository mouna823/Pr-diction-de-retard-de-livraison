# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G2  ·  **Membres :** ESSIFI Aymene  ·  **Date :** 09/11/2026

Compte rendu complété à partir de l'exécution du projet et de ses tests. Le jeu de
données affiché ci-dessous est celui généré par `python -m maintai.dataset`
(`n=5000`, `seed=42`, valeurs par défaut). Groupe G2, membre : ESSIFI Aymene.

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
5 failed, 18 passed
```

Quels fichiers de tests échouaient, et quelle erreur donnaient-ils ?

- `tests/test_client.py` : trois échecs `NotImplementedError`, car `MaintaiClient.predict`
  n'était pas implémentée.
- `tests/test_ui.py` : deux échecs `IndexError`, car l'interface ne créait encore
  aucun indicateur ni résultat de prédiction.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
Sans activer l'environnement virtuel, PowerShell ne trouve pas la commande
`streamlit` dans le `PATH` : le serveur ne démarre donc pas et aucune page ne s'ouvre.
```

Avec `.\.venv\Scripts\python.exe -m streamlit run ui/app.py`, Streamlit 1.66.1 démarre
et la page MaintAI s'ouvre à `http://localhost:8501`. Elle présente les onglets
« Données » et « Prédiction ». Le CSV doit avoir été généré au préalable.

`python -m streamlit` démarre le module avec l'interpréteur choisi explicitement.
La commande courte dépend de la présence du dossier `Scripts` de l'environnement
virtuel dans le `PATH` (ou de l'activation de cet environnement).

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", len(df))
c2.metric("Taux de panne", f"{df['failure'].mean():.1%}")
c3.metric("Température moyenne", f"{df['temperature_c'].mean():.1f} °C")

variable = st.selectbox("Variable à analyser", FEATURES)
tranches = pd.cut(df[variable], bins=10)
taux_par_tranche = df.groupby(tranches, observed=True)["failure"].mean()
taux_par_tranche.index = [round(interval.mid, 2) for interval in taux_par_tranche.index]
st.bar_chart(taux_par_tranche)

donnees_nuage = df.assign(etat=df["failure"].map({0: "Normal", 1: "Panne"}))
st.scatter_chart(
    donnees_nuage,
    x="temperature_c",
    y="vibration_mm_s",
    color="etat",
)
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6 % |
| Température moyenne | 59.8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente nettement avec la vibration : il est d'environ 2 % dans la
première tranche, dépasse 32 % dans la troisième, puis 80 % dans les tranches élevées.
Certaines tranches n'ont pas de relevés. Cette tendance correspond à la formule de
risque utilisée pour générer ces données synthétiques ; elle ne prouve pas une
causalité dans des données réelles.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

À chaque interaction, le script est réexécuté et `print("relance")` réapparaît
dans le terminal. Cela illustre le modèle de rerun de Streamlit.

`@st.cache_data` mémorise le résultat de la lecture du CSV pour un même chemin et
évite de relire le fichier à chaque rerun.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
headers = {"X-API-Key": self.api_key} if self.api_key else {}
response = self.http.post("/v1/predict", json=reading, headers=headers)
if response.status_code != 200:
    try:
        body = response.json()
    except ValueError:
        body = {}
    detail = body.get("detail", response.text) if isinstance(body, dict) else body
    raise APIError(response.status_code, detail)
return response.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
23 passed, 1 warning
```

Avec l'API lancée (`.\.venv\Scripts\python.exe -m uvicorn maintai.api.main:app --reload --env-file .env`),
la santé de l'API répond `200 OK` avec `model_loaded: true`. Pour le relevé par
défaut (`72 °C`, `6 mm/s`, `85 %`, `15000` heures), l'API renvoie une probabilité
de `0.9475` et déclenche l'alerte :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, clé configurée dans `.env` | Probabilité : 95 % ; alerte de panne |
| valeurs par défaut, fausse clé | Avertissement `Erreur 401 : Clé API absente ou invalide` |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Erreur `API injoignable` |

La nouvelle clé configurée dans `.env` a été vérifiée sur l'API du port `8001` :
la prédiction autorisée répond `200` et une clé invalide répond `401`. Le port
`8000` était occupé par une ancienne API ; la nouvelle instance a donc été lancée sur
`8001`. Il faut saisir `http://127.0.0.1:8001` dans la barre latérale de Streamlit
pour appeler cette instance.

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

Streamlit envoie la requête depuis son processus Python vers l'API ; le navigateur
ne contacte pas directement l'API. CORS est une restriction appliquée par les
navigateurs aux requêtes inter-origines, pas par le client HTTP Python.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   Dans le TP2, c'est le navigateur via JavaScript (`fetch`). Dans Streamlit, c'est
   le processus Python via `MaintaiClient`.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   Ils injectent le client de test FastAPI dans `MaintaiClient` ; la requête est
   adressée directement à l'application en mémoire.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   Pour une démonstration rapide, Streamlit permet de présenter facilement les
   graphiques et la prédiction. Pour un outil destiné aux techniciens, le choix
   dépend des besoins d'ergonomie et de déploiement : HTML/JavaScript offre plus de
   contrôle sur l'expérience utilisateur, tandis que Streamlit permet de faire
   évoluer rapidement une interface métier interne.

## 6. Le rendu Git

- Lien de la pull request : aucune pull request créée.
- Le tag `tp3` existe sur GitHub : non vérifié ; aucun tag local ou dépôt distant
  n'est configuré dans ce dossier.
- `git status` : le dossier TP3 n'est pas initialisé comme dépôt Git indépendant.
  Les fichiers du projet apparaissent non suivis dans le dépôt parent ; `.env`,
  `data/*.csv` et `models/` sont ignorés par les règles du `.gitignore` local.
- Aucun commit ni push n'a été effectué.

## 7. Ce qui reste flou

Le code et les tests du TP3 sont terminés (`23 passed`). Il reste au groupe à
renseigner ses noms, puis à initialiser/configurer le dépôt distant, créer la pull
request, la faire relire et fusionner, et publier le tag `tp3`.
