# main.py — AllRoad’s API
from fastapi import FastAPI

app = FastAPI(
    title="AllRoad’s API",
    description="API de calcul et affichage d’itinéraire",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Bienvenue sur AllRoad’s API"}

@app.get("/route")
def get_route():
    return {
        "route_name": "Ille-sur-Têt → Thuir",
        "coordinates": [
            [42.670, 2.620],
            [42.635, 2.760]
        ],
        "distance_km": 12.5,
        "duration_min": 18,
        "transport_mode": "car"
    }

@app.get("/status")
def status():
    return {"status": "API opérationnelle", "version": "1.0.0"}
