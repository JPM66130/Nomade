from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# ---------------------------
#  MIDDLEWARE DE SÉCURITÉ
# ---------------------------

@app.middleware("http")
async def access_control(request: Request, call_next):

    # 1. Routes publiques (pas de token)
    public_paths = [
        "/status",
        "/stations",
        "/station",
    ]

    path = request.url.path

    # Si la route commence par un chemin public → OK
    if any(path.startswith(p) for p in public_paths):
        return await call_next(request)

    # 2. Mode développeur (dev=3647)
    dev = request.query_params.get("dev")
    if dev == "3647":
        return await call_next(request)

    # 3. Token obligatoire pour les autres routes
    token_env = os.getenv("API_ACCESS_TOKEN")  # Render
    token_user = request.query_params.get("token")

    # Si pas de token défini dans Render → sécurité OFF (local)
    if not token_env:
        return await call_next(request)

    # Si token utilisateur incorrect → bloqué
    if token_user != token_env:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token d'accès requis ou invalide."}
        )

    # 4. Token correct → OK
    return await call_next(request)
