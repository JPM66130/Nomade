# Nomade – API FastAPI

![Tests](https://github.com/JPM66130/Nomade/actions/workflows/test-app.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)

API pour les voyageurs nomades : stations, spots, parkings, alertes et itinéraires.

---

## 📦 Installation locale

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

L'API est accessible sur : http://localhost:8000

---

## 🧪 Tests

```bash
pytest --disable-warnings
```

---

## 🚀 Déploiement Render

Le fichier `render.yaml` à la racine configure automatiquement le déploiement :

- **Runtime** : Python 3.11
- **Build** : `pip install -r requirements.txt`
- **Start** : `uvicorn main:app --host 0.0.0.0 --port $PORT`

Pour déployer :
1. Connectez-vous sur [render.com](https://render.com)
2. Créez un nouveau service web en pointant sur ce dépôt
3. Render détecte automatiquement `render.yaml`

---

## 📡 Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Statut de l'API |
| GET | `/pays` | Liste des pays |
| GET | `/pays/{id}` | Détail d'un pays |
| GET | `/stations` | Liste des stations |
| GET | `/parkings` | Liste des parkings |
| GET | `/spots` | Spots nomades |
| GET | `/alertes` | Alertes en cours |
| GET | `/itineraire?depart=A&arrivee=B` | Calcul d'itinéraire |

---

## 📂 Structure du projet

```
.
├── main.py              # Application FastAPI
├── requirements.txt     # Dépendances Python
├── render.yaml          # Configuration déploiement Render
├── tests/               # Tests pytest
└── .github/workflows/
    └── test-app.yml     # CI GitHub Actions
```
