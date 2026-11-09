# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :**
**Membres :** ZIDANI RIHABE 
**Date :** 09/11/2026

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```text
[À compléter : résultat du premier lancement de pytest immédiatement après l'installation des requirements]
```

**Quels sont les deux tests qui échouent, et pourquoi ?**

Les deux tests qui échouent doivent être identifiés à partir de la sortie du premier lancement de `pytest`. Cette sortie n'a pas encore été récupérée. Il faut donc vérifier les erreurs affichées pour expliquer précisément leur origine.

---

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

**Vos sections `dependencies` et `[project.scripts]` :**

```toml
dependencies = [
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27"
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

**Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?**

`pytest` est un outil de développement et de test. Il n'est pas nécessaire pour utiliser le package en production. Il est donc placé dans les dépendances optionnelles de développement (`dev`).

`fastapi` est nécessaire uniquement pour la partie API du projet. Il est donc placé dans les dépendances optionnelles (`api`) et non dans les dépendances principales.

**Sortie de `pip show maintai` (les quatre premières lignes) :**

```text
Name: maintai
Version: 0.2.0
Summary: Python package for machine learning-based predictive maintenance
Author-email:
```

**Dernière ligne de `python -m pytest` à la fin du sprint 1 :**

```text
27 passed, 1 warning in 15.85s
```

**Test depuis un autre dossier (`cd %TEMP%`) :**

Après l'installation avec `pip install -e .`, la commande :

```powershell
maintai-predict 72 6 85 15000
```

affiche :

```text
Probabilité de panne : 95 % (ALERTE)
```

La commande :

```powershell
python -c "import maintai; print(maintai.__file__)"
```

affiche :

```text
C:\Users\ZIDANI RIHAB\Downloads\TP4\maintai-starter-tp4\maintai\__init__.py
```

Python trouve donc le code source dans le dossier original du projet, même si la commande est exécutée depuis `%TEMP%`.

**Conclusion :** l'installation en mode éditable (`pip install -e .`) permet d'utiliser le package depuis un autre dossier tout en conservant un lien direct avec le code source du projet.

**Modification du message dans `maintai/cli.py` :**

[À compléter après avoir modifié temporairement le message dans `cli.py` et relancé `maintai-predict` sans réinstaller.]

Explication attendue : avec une installation éditable, les modifications du code source sont normalement visibles directement, sans réinstallation du package.

---

## 3. Sprint 2 : construire et installer le wheel

**Sortie de `dir dist` après `python -m build` :**

```text
maintai-0.2.0-py3-none-any.whl
maintai-0.2.0.tar.gz
```

**Contenu du wheel :**

Le wheel contient le package Python `maintai/` ainsi que les métadonnées d'installation dans le dossier `maintai-0.2.0.dist-info/`.

Le modèle, les tests et le dossier `ui/` ne sont pas inclus.

**Pourquoi ?**

La configuration de `pyproject.toml` contient :

```toml
[tool.setuptools.packages.find]
include = ["maintai*"]
```

Cette configuration indique à setuptools de rechercher et d'inclure les packages dont le nom commence par `maintai`. Les dossiers du modèle, des tests et de l'interface utilisateur ne sont donc pas intégrés au wheel.

**Installation dans un environnement neuf (`%TEMP%\essai`) :**

| Étape | Ce qui s'affiche |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : C:\Users\ZIDANI RIHAB\Downloads\TP4\models\model.joblib` |
| Avec `MAINTAI_MODELS_DIR` configuré vers le dossier `models` du projet | `Probabilité de panne : 95 % (ALERTE)` |
| Après `pip install scikit-learn==1.8.0` | La version installée est `1.8.0`. Le modèle peut être chargé avec cette version ; la commande de prédiction affiche `Probabilité de panne : 95 % (ALERTE)`. |

**D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?**

Cet avertissement peut apparaître lorsque le modèle a été entraîné avec une version de Scikit-learn différente de celle utilisée pour le charger.

Dans notre fichier `models/model_info.json`, on trouve