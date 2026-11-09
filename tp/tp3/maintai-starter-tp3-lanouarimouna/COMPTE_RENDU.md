# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

=============================== 5 failed, 18 passed, 1 warning in 5.44s ================================


Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

`tests/test_client.py` (3 tests) : `MaintaiClient.predict` lève `NotImplementedError: TP3 sprint 2 : MaintaiClient.predict`,
car la méthode n'est pas encore écrite.
`tests/test_ui.py` (2 tests) : `test_ui_shows_the_data` échoue car l'onglet « Données » n'a pas encore d'indicateur
(`at.metric[0]` n'existe pas) ; `test_ui_shows_the_prediction` échoue car rien ne s'affiche après le clic sur « Prédire ».

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

ModuleNotFoundError: No module named 'maintai'
Traceback:
File "C:\Users\LENOVO\Downloads\TP3\maintai-starter-tp3\ui\app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

2026-11-09 09:53:39.606 Uvicorn server started on :::8502

  You can now view your Streamlit app in your browser.

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

# Sprint 1 : explorer les données
with onglet_donnees:
    df = charger(get_settings().data_path)

    # 1. Trois indicateurs côte à côte (le 1er DOIT être le nombre de relevés : le test le lit)
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
    c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

    # 2. Liste déroulante pour choisir la variable
    variable = st.selectbox("Variable", FEATURES)

    # 3. Taux de panne par tranche, en barres
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True).failure.mean()
    taux.index = [round(i.mid) for i in taux.index]   # nombres, pas du texte (sinon ordre bizarre)
    st.bar_chart(taux)

    # 4. Nuage de points température / vibration, coloré selon la panne
    df_nuage = df.copy()
    df_nuage["panne"] = df_nuage.failure.map({0: "non", 1: "oui"})
    st.scatter_chart(df_nuage, x="temperature_c", y="vibration_mm_s", color="panne")

| Indicateur | Valeur affichée |
|---|---|
| Relevés |5000 |
| Taux de panne |13.6% |
| Température moyenne |59.8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne est très faible pour les petites vibrations, puis il augmente fortement pour les tranches les plus
élevées [adaptez : ex. jusqu'à environ ... % dans la dernière tranche]. La température suit la même tendance.
[Laquelle compte le plus ? Comparez la hauteur maximale des barres des deux variables, et dites celle dont
les barres montent le plus haut / le plus nettement.]

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

À chaque interaction avec un widget (liste déroulante, bouton), « relance » s'affiche de nouveau dans le terminal.
Streamlit exécute donc tout le script ui/app.py, de la première à la dernière ligne, à chaque interaction.
[Si vous bougez un curseur à l'intérieur d'un `st.form`, rien ne s'affiche : seul le bouton « Prédire » relance.]

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Comme le script est relancé à chaque clic, sans cache le CSV serait relu à chaque fois. Avec `@st.cache_data`,
la fonction ne s'exécute qu'une fois ; ensuite Streamlit renvoie le même tableau gardé en mémoire : la page est plus rapide.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

    def predict(self, reading: dict) -> dict:
        """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        r = self.http.post("/v1/predict", json=reading, headers=headers)
        if r.status_code != 200:
            raise APIError(r.status_code, r.json().get("detail"))
        return r.json()

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

==================================== 23 passed, 1 warning in 8.82s =====================================

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Fonctionnement normal|
| valeurs par défaut, fausse clé |Erreur 401 : Clé API absente ou invalide |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) |API injoignable : uvicorn est-il lancé ?|

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

CORS est une règle du NAVIGATEUR : en TP2, `fetch` s'exécutait dans le navigateur, qui vérifiait l'origine de la page
(port 5501) auprès de l'API. Avec Streamlit, le navigateur ne fait qu'afficher la page et n'appelle jamais l'API : c'est le
serveur Streamlit (Python, via httpx) qui envoie la requête, comme curl ou Java. Il n'y a pas d'en-tête Origin ni de
contrôle CORS. L'API vérifie toujours la clé `X-API-Key`.

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?

   TP2 : le navigateur de l'utilisateur (JavaScript, `fetch`), donc soumis à CORS. Streamlit : le serveur Streamlit
   (Python, `MaintaiClient` avec httpx) ; le navigateur n'appelle jamais l'API.

2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?

   Parce qu'on donne à `MaintaiClient` le client de test de la séance 5 (`http=client`) : la requête va directement
   à l'application FastAPI en mémoire, sans réseau ni serveur. C'est possible car `predict` utilise `self.http.post`,
   pas `httpx.post`.

3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?

   Démonstration à un client : la page HTML + JavaScript, car on maîtrise entièrement l'apparence (image de marque,
   rendu soigné) et elle est légère, sans serveur Python. Technicien de maintenance : Streamlit, car il combine données
   et prédiction dans une interface fonctionnelle, écrite en Python, prête en une séance et facile à faire évoluer
   par l'équipe, qui ne connaît pas forcément JavaScript. Contrepartie : moins de personnalisation visuelle.

## 6. Le rendu Git

- Lien de la pull request : …
- Le tag `tp3` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? oui / non

## 7. Ce qui reste flou

…
