from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# ---------------------------
#  MIDDLEWARE DE SÉCURITÉ
# ---------------------------

@app.middleware("http")
async def access_control(request: Request, call_next):

    path = request.url.path

    # 1. Routes publiques
    public_paths = [
        "/status",
        "/stations",
        "/station",
    ]

    if any(path.startswith(p) for p in public_paths):
        return await call_next(request)

    # 2. Mode développeur
    dev = request.query_params.get("dev")
    if dev == "3647":
        return await call_next(request)

    # 3. Token Render
    token_env = os.getenv("API_ACCESS_TOKEN")
    token_user = request.query_params.get("token")

    # En local → pas de token → sécurité OFF
    if not token_env:
        return await call_next(request)

    # Token incorrect
    if token_user != token_env:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token d'accès requis."}
        )

    return await call_next(request)


# ---------------------------
#  ROUTES
# ---------------------------

@app.get("/status")
def status():
    return {"message": "Nomade bêta opérationnelle"}


@app.get("/stations")
def stations():
    return {"message": "Liste des stations (exemple)"}


@app.get("/station/{id}")
def station(id: int):
    return {"message": f"Station {id}"}


@app.get("/proche")
def proche(lat: float, lon: float):
    return {"message": "Station proche (exemple)"}


# ---------------------------
#  DÉMARRAGE LOCAL
# ---------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
