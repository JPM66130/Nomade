from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI(
    title="Nomade / AllRoad’s API",
    description="API officielle du projet Nomade / AllRoad’s",
    version="1.0.0"
)

# ---------------------------------------------------------
# ROUTE DE TEST (pour GitHub Actions et pytest)
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "API Nomade / AllRoad’s opérationnelle"}


# ---------------------------------------------------------
# ROUTES : PAYS
# ---------------------------------------------------------
fake_pays = [
    {"id": 1, "nom": "France"},
    {"id": 2, "nom": "Espagne"},
    {"id": 3, "nom": "Maroc"}
]

@app.get("/pays", response_model=List[Dict])
def get_pays():
    return fake_pays


@app.get("/pays/{pays_id}", response_model=Dict)
def get_pays_by_id(pays_id: int):
    for p in fake_pays:
        if p["id"] == pays_id:
            return p
    raise HTTPException(status_code=404, detail="Pays introuvable")


# ---------------------------------------------------------
# ROUTES : STATIONS (essence, GPL, etc.)
# ---------------------------------------------------------
fake_stations = [
    {"id": 1, "nom": "Total Ille-sur-Têt", "pays": "France"},
    {"id": 2, "nom": "CEPSA Figueres", "pays": "Espagne"},
]

@app.get("/stations", response_model=List[Dict])
def get_stations():
    return fake_stations


# ---------------------------------------------------------
# ROUTES : PARKINGS / AIRES
# ---------------------------------------------------------
fake_parkings = [
    {"id": 1, "nom": "Aire de Néfiach", "type": "camping-car"},
    {"id": 2, "nom": "Parking Vernet-les-Bains", "type": "public"},
]

@app.get("/parkings", response_model=List[Dict])
def get_parkings():
    return fake_parkings


# ---------------------------------------------------------
# ROUTES : SPOTS (points d’intérêt)
# ---------------------------------------------------------
fake_spots = [
    {"id": 1, "nom": "Gorges de la Carança", "categorie": "randonnée"},
    {"id": 2, "nom": "Lac de Vinça", "categorie": "nature"},
]

@app.get("/spots", response_model=List[Dict])
def get_spots():
    return fake_spots


# ---------------------------------------------------------
# ROUTES : ALERTES (sécurité, météo, trafic)
# ---------------------------------------------------------
fake_alertes = [
    {"id": 1, "type": "météo", "message": "Fortes rafales de vent sur le Canigou"},
    {"id": 2, "type": "trafic", "message": "Bouchon sur l’A9 direction Barcelone"},
]

@app.get("/alertes", response_model=List[Dict])
def get_alertes():
    return fake_alertes


# ---------------------------------------------------------
# ROUTES : ITINÉRAIRES (simple version)
# ---------------------------------------------------------
@app.get("/itineraire")
def itineraire(depart: str, arrivee: str):
    return {
        "depart": depart,
        "arrivee": arrivee,
        "distance_km": 42,
        "temps_estime": "45 minutes",
        "message": "Itinéraire calculé (version simplifiée)"
    }


# ---------------------------------------------------------
# DÉMARRAGE UVICORN (optionnel)
# ---------------------------------------------------------
# À utiliser uniquement si tu lances l’API en local :
# uvicorn main:app --reload
