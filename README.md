# Nomade – API officielle

![Tests](https://github.com/JPM66130/Nomade/actions/workflows/test-app.yml/badge.svg)

Nomade est une API pensée pour les voyageurs.  
Elle fournit des données sur les stations, spots, parkings, alertes et itinéraires.

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

---

## ☁️ Déploiement sur Render (Blueprint)

Le dépôt inclut un fichier `render.yaml` à la racine pour créer un **Web Service** Render.

1. Ouvrir Render : **New + → Blueprint**
2. Sélectionner le repo `JPM66130/Nomade`
3. Renseigner :
   - **Branch** : `main`
   - **Blueprint Path** : `render.yaml`
4. Lancer le déploiement

Configuration utilisée :
- Build : `pip install --upgrade pip && if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install fastapi uvicorn; fi`
- Start : `uvicorn main:app --host 0.0.0.0 --port $PORT`
