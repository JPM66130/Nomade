from pathlib import Path
from collections import defaultdict, deque
import hmac
import os
from threading import Lock
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from db import Base, engine
from routers import pays, stations, spots, parkings, peages, restrictions, alertes, itineraires

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
else:
    API_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT == "production" and not API_ACCESS_TOKEN:
    raise RuntimeError("API_ACCESS_TOKEN est obligatoire en production")

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
request_times = defaultdict(deque)
rate_limit_lock = Lock()


@app.middleware("http")
async def protect_api(request: Request, call_next):
    public_paths = {"/", "/health", "/docs", "/docs/oauth2-redirect", "/openapi.json"}
    client_host = request.client.host if request.client else None
    is_local_request = client_host in {"127.0.0.1", "::1"}
    if API_ACCESS_TOKEN and not is_local_request and not request.url.path.startswith("/app") and request.url.path not in public_paths:
        authorization = request.headers.get("Authorization", "")
        supplied_token = authorization.removeprefix("Bearer ").strip()
        if not hmac.compare_digest(supplied_token.encode("utf-8"), API_ACCESS_TOKEN.encode("utf-8")):
            return JSONResponse({"detail": "Token d'accès requis."}, status_code=401)
    if not is_local_request and not request.url.path.startswith("/app") and request.url.path not in public_paths:
        now = time.monotonic()
        with rate_limit_lock:
            recent_requests = request_times[client_host]
            while recent_requests and recent_requests[0] <= now - 60:
                recent_requests.popleft()
            if len(recent_requests) >= RATE_LIMIT_PER_MINUTE:
                return JSONResponse({"detail": "Trop de requêtes. Réessayez dans une minute."}, status_code=429)
            recent_requests.append(now)
    return await call_next(request)

Base.metadata.create_all(bind=engine)

app.include_router(pays.router)
app.include_router(stations.router)
app.include_router(spots.router)
app.include_router(parkings.router)
app.include_router(peages.router)
app.include_router(restrictions.router)
app.include_router(alertes.router)
app.include_router(itineraires.router)

app.mount(
    "/app",
    StaticFiles(directory=Path(__file__).parent / "frontend", html=True),
    name="frontend",
)

@app.get("/")
def root():
    return {"message": "Nomade bêta opérationnelle"}


@app.get("/health")
def health():
    return {"status": "ok"}
