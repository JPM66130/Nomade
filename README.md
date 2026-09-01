# Nomade – API officielle

![Tests](https://github.com/JPM66130/Nomade/actions/workflows/test-app.yml/badge.svg)

Nomade est une API pensée pour les voyageurs.  
Elle fournit des données sur les stations, spots, parkings, alertes et itinéraires.

---

## ⚙️ Installation

### Prérequis
- Python 3.11+
- pip

### Étapes
1. Cloner le dépôt
2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## ▶️ Démarrage en local

Lancer l’API avec Uvicorn :

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API accessible sur : `http://localhost:8000`

---

## 🐳 Déploiement Docker

### Avec Docker
```bash
docker build -t nomade-api .
docker run --env-file .env -p 8000:8000 nomade-api
```

### Avec Docker Compose
```bash
docker compose up --build
```

---

## 🚀 Déploiement en production

Recommandations :
- Utiliser `ENVIRONMENT=production`
- Définir les variables d’environnement via l’infrastructure (et non en dur)
- Placer l’API derrière un reverse proxy (Nginx/Caddy) avec HTTPS
- Mettre en place la supervision (logs, santé, alertes)
- Conserver les tests CI activés avant toute mise en production

---

## 🚀 Fonctionnalités principales

- Calcul d’itinéraires selon le type de véhicule  
- Estimation carburant, péages, ferries  
- Carte interactive  
- Mode navigation conducteur  
- Géocodage d’adresses  
- Endpoints rapides et optimisés  

---

## 🧪 Tests automatisés (CI GitHub Actions)

Les tests sont exécutés automatiquement à chaque push :

- ✔️ Tests d’erreurs (404, 422)  
- ✔️ Tests de filtres  
- ✔️ Tests de performance  
- ✔️ Tests de structure JSON  
- ✔️ Tests de valeurs invalides  
- ✔️ Tests de routes inexistantes  

---

## 📂 Structure du projet

![Tests](https://github.com/JPM66130/Nomade/actions/workflows/test-app.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Coverage](https://github.com/JPM66130/Nomade/raw/main/coverage.svg)

## 📡 Endpoints principaux

### 🔍 Stations
`GET /stations`
→ Retourne la liste complète des stations.

`GET /stations/{id}`
→ Retourne une station spécifique.

### 🅿️ Parkings
`GET /parkings`
→ Liste des parkings disponibles.

### 🏕️ Spots nomades
`GET /spots`
→ Spots nomades, bivouacs, lieux de pause.

### ⚠️ Alertes
`GET /alerts`
→ Alertes routières, météo, incidents.

### 🛣️ Itinéraires
`GET /route?from=A&to=B&type=car`
→ Calcul d’itinéraire selon le véhicule.

### 🧭 Géocodage
`GET /geocode?query=adresse`
→ Convertit une adresse en coordonnées GPS.
