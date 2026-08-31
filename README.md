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
