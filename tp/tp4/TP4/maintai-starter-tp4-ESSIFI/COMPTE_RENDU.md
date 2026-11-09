# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G2  ·  **Membres :** Essifi Aymene  ·  **Date :** 09/11/2026

> Les commandes de test et d'installation mentionnées ci-dessous ont été vérifiées sur le projet.
> Les résultats de l'essai dans un environnement neuf sont indiqués comme résultats attendus :
> cet environnement séparé n'a pas été créé.

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Après `pip install -r requirements.txt`, les deux tests du package qui échouent sont :

- `test_installed_version_matches_the_code` : MaintAI n'a pas encore été installé, donc les métadonnées de distribution ne sont pas trouvées.
- `test_command_is_declared` : le point d'entrée `maintai-predict` n'est pas encore installé.

Résultat attendu avant `pip install -e .` :

```
2 failed, 25 passed
```

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "numpy>=2.4",
    "pandas>=3.0",
    "scikit-learn>=1.8",
    "joblib>=1.5",
    "httpx>=0.28",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

`pytest` est un outil de développement et n'est pas nécessaire pour utiliser le package.
`fastapi` est nécessaire uniquement pour l'API : il est donc proposé dans l'extra optionnel `api`.

Quatre premières lignes de `pip show maintai` après `pip install -e .` :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de pannes à partir de relevés de capteurs
Home-page:
```

Dernière ligne de `python -m pytest -q` après installation éditable :

```
27 passed
```

Depuis `%TEMP%`, `python -c "import maintai; print(maintai.__file__)"` affiche le chemin du fichier
`maintai/__init__.py` dans le dossier du projet. C'est l'installation éditable (`pip install -e .`)
qui permet à Python de trouver le code source à cet emplacement.

Exemple de prédiction depuis le terminal :

```
Probabilité de panne : 95 % (ALERTE)
```

Dans cet environnement, `maintai-predict` n'est pas reconnu directement car le dossier `Scripts`
de l'installation utilisateur n'est pas dans `PATH`. L'exécutable a été installé ici :
`C:\Users\ayman\AppData\Roaming\Python\Python313\Scripts\maintai-predict.exe`.
En ajoutant ce dossier au `PATH` (ou en appelant l'exécutable avec son chemin complet), la commande
fonctionne. Avec une installation éditable, modifier `maintai/cli.py` est visible sans réinstaller :
la commande charge directement le code source du projet.

## 3. Sprint 2 : construire et installer le wheel

Contenu de `dist` après `python -m build` :

```
maintai-0.2.0-py3-none-any.whl
maintai-0.2.0.tar.gz
```

Fichiers contenus dans `maintai-0.2.0-py3-none-any.whl` :

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le wheel ne contient ni le modèle, ni les tests, ni `ui/`. La recherche de paquets dans
`pyproject.toml` inclut uniquement `maintai*`; les autres éléments ne font pas partie du package.

Résultats attendus dans l'environnement neuf, après installation du wheel et activation de son
environnement :

| Étape | Ce qui s'affiche |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | Modèle introuvable dans le dossier par défaut du package ; le programme indique de définir `MAINTAI_MODELS_DIR`. |
| Avec `MAINTAI_MODELS_DIR` vers le dossier `models` du projet | `Probabilité de panne : 95 % (ALERTE)` pour `72 6 85 15000`. |
| Après `pip install scikit-learn==1.8.0` | Même prédiction ; la version correspond à celle utilisée pour entraîner le modèle, donc l'avertissement de version incohérente ne devrait plus apparaître. |

Un avertissement `InconsistentVersionWarning` signifie que scikit-learn charge un modèle sérialisé
avec une version différente de celle actuellement installée. Dans `models/model_info.json`, la ligne
qui renseigne la version d'entraînement est :

```json
"sklearn_version": "1.8.0"
```

## 4. Questions de compréhension

1. `requirements.txt` fige les versions utilisées pour reproduire l'environnement du projet.
   `dependencies` dans `pyproject.toml` déclare les bibliothèques nécessaires à l'installation
   du package, avec des versions minimales.
2. `pip install -e .` installe le projet en mode éditable et utilise son code source sur place.
   `pip install dist\maintai-0.2.0-py3-none-any.whl` installe une distribution construite,
   indépendante du dossier source.
3. `[project.scripts]` déclare une commande terminal associée à une fonction Python.
   Ici, `maintai-predict` appelle `maintai.cli:main`. Sur cette machine, pip crée
   `maintai-predict.exe` dans
   `C:\Users\ayman\AppData\Roaming\Python\Python313\Scripts`.

## 5. Le rendu Git

- Lien de la pull request : aucune pull request créée (aucun remote Git n'est configuré).
- Le tag `tp4` existe sur GitHub : non ; aucun tag local `tp4` n'est présent non plus.
- `git status` avant le commit : `dist/`, `build/` et `maintai.egg-info/` sont ignorés par `.gitignore` et n'apparaissent pas dans le statut normal. Les fichiers du projet apparaissent toutefois comme non suivis dans ce dépôt local.

## 6. Ce qui reste flou

Les étapes d'installation du wheel et de comparaison des versions dans un environnement neuf
restent à exécuter pour confirmer les résultats attendus de la section 3.
