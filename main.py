from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
import os

app = FastAPI(
    title="AllRoads API",
    description="API Nomade (version stable)",
    version="1.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Chargement des données ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "stations.json")

def load_stations():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

STATIONS = load_stations()

# --- ROUTES ---

@app.get("/status")
def status():
    return {"status": "OK", "message": "Nomade opérationnelle"}

@app.get("/stations")
def get_stations(dev: int = Query(None)):
    if dev == 3647:
        return {"status": "OK", "stations": STATIONS}
    return {"status": "ERROR", "message": "Paramètre dev incorrect ou manquant"}

@app.get("/station/{station_id}")
def get_station(station_id: int, dev: int = Query(None)):
    if dev != 3647:
        return {"status": "ERROR", "message": "Paramètre dev incorrect ou manquant"}

    for s in STATIONS:
        if s["id"] == station_id:
            return {"status": "OK", "station": s}
    return {"status": "ERROR", "message": "Station introuvable"}

@app.get("/proche")
def get_proche(lat: float, lon: float, dev: int = Query(None)):
    if dev != 3647:
        return {"status": "ERROR", "message": "Paramètre dev incorrect ou manquant"}

    # Algo simplifié (distance réelle plus tard)
    return {"status": "OK", "stations": STATIONS}

# --- Lancement local ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
