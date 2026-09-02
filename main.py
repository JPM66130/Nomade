from pathlib import Path
from collections import defaultdict, deque
import hmac
import os
import threading
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from dotenv import load_dotenv

from db import Base, engine
from outers import pays, stations, spots, parkings, peages, restrictions, alertes, itineraires


# ---------------------------------------------------------
# 🔧 CONFIGURATION DE L’API
# ---------------------------------------------------------
app = FastAPI(title="Nomade bêta")

env_path = Path(__file__).parent / "clé.env"
load_dotenv(env_path)
load_dotenv(Path(__file__).parent / ".env")

if env_path.is_file():
    with env_path.open(encoding="utf-8") as env_file:
        API_ACCESS_TOKEN = next(
            (line.split("=", 1)[1].strip() for line in env_file if line.startswith("API_ACCESS_TOKEN=")),
            None,
        )

API_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "production" and not API_ACCESS_TOKEN:
    raise RuntimeError("API_ACCESS_TOKEN est obligatoire en production")


# ---------------------------------------------------------
# 🔐 CODE DÉVELOPPEUR (accès temporaire)
# ---------------------------------------------------------
CODE_DEV = "3647"   # ton code développeur


# ---------------------------------------------------------
# 🔐 MIDDLEWARE GLOBAL — Sécurité + accès développeur
# ---------------------------------------------------------
RATE_LIMIT_PER_MINUTE = 60
rate_limit_lock = threading.Lock()
request_times = defaultdict(deque)

public_paths = {"/health", "/app", "/"}

@app.middleware("http")
async def global_security(request: Request, call_next):
    client_host = request.client.host
    path = request.url.path

    # 1️⃣ Accès développeur : bypass total
    if request.query_params.get("dev") == CODE_DEV:
        return await call_next(request)

    # 2️⃣ Accès local (localhost)
    is_local_request = client_host in {"127.0.0.1", "::1"}

    # 3️⃣ Vérification du token (production)
    if API_ACCESS_TOKEN and not is_local_request and path not in public_paths:
        authorization = request.headers.get("Authorization", "")
        supplied_token = authorization.removeprefix("Bearer ").strip()

        if not hmac.compare_digest(supplied_token.encode("utf-8"), API_ACCESS_TOKEN.encode("utf-8")):
            return JSONResponse({"detail": "Token d'accès requis"}, status_code=401)

    # 4️⃣ Rate-limit
    if not is_local_request and path not in public_paths:
        now = time.monotonic()
        with rate_limit_lock:
            recent_requests = request_times[client_host]
            while recent_requests and recent_requests[0] <= now - 60:
                recent_requests.popleft()

            if len(recent_requests) >= RATE_LIMIT_PER_MINUTE:
                return JSONResponse({"detail": "Trop de requêtes. Réessayez dans une minute."}, status_code=429)

            recent_requests.append(now)

    return await call_next(request)


# ---------------------------------------------------------
# 🟪 MISE À JOUR AUTOMATIQUE DES TABLES SQLITE
# ---------------------------------------------------------
if engine.dialect.name == "sqlite" and "arrets" in inspect(engine).get_table_names():
    stop_columns = {column["name"] for column in inspect(engine).get_columns("arrets")}
    if "nom" not in stop_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE arrets ADD COLUMN nom VARCHAR NOT NULL DEFAULT 'Arrêt'"))

if engine.dialect.name == "sqlite" and "trajet_details" in inspect(engine).get_table_names():
    trip_detail_columns = {column["name"] for column in inspect(engine).get_columns("trajet_details")}
    if "nom_tournee" not in trip_detail_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE trajet_details ADD COLUMN nom_tournee VARCHAR NOT NULL DEFAULT 'Tournee'"))


# ---------------------------------------------------------
# 📦 ROUTERS
# ---------------------------------------------------------
app.include_router(pays.router)
app.include_router(stations.router)
app.include_router(spots.router)
app.include_router(parkings.router)
app.include_router(peages.router)
app.include_router(restrictions.router)
app.include_router(alertes.router)
app.include_router(itineraires.router)


# ---------------------------------------------------------
# 🌐 FRONTEND
# ---------------------------------------------------------
app.mount(
    "/app",
    StaticFiles(directory=Path(__file__).parent / "frontend", html=True),
    name="frontend",
)


# ---------------------------------------------------------
# 🏠 ROUTES DE BASE
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Nomade bêta opérationnelle"}

@app.get("/health")
def health():
    return {"status": "ok"}
