# main.py — AllRoad’s API
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="AllRoad’s API",
    description="API de calcul et affichage d’itinéraire",
    version="1.0.0"
)

# Code développeur temporaire (à changer par ton code perso)
CODE_DEV = "3647"


@app.get("/")
def home():
    return {"message": "Bienvenue sur AllRoad’s API"}


@app.get("/route")
def get_route(dev: str | None = None):
    # Accès développeur
    if dev == CODE_DEV:
        return {
            "route_name": "Ille-sur-Têt -> Thuir",
            "coordinates": [
                [42.670, 2.620],
                [42.635, 2.760]
            ],
            "distance_km": 12.5,
            "duration_min": 18,
            "transport_mode": "car"
        }

    # Sécurité normale
    raise HTTPException(status_code=401, detail="Token d'accès requis.")


@app.get("/status")
def status():
    return {"status": "API opérationnelle", "version": "1.0.0"}
