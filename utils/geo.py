import math
import logging
import os
import json
import urllib.parse
import urllib.request

from dotenv import load_dotenv

try:
    import openrouteservice
except ImportError:
    openrouteservice = None


logger = logging.getLogger(__name__)

ORS_PROFILES = {
    "pieton": "foot-walking",
    "velo": "cycling-regular",
    "voiture": "driving-car",
    "4x4": "driving-car",
    "camping_car": "driving-car",
    "poids_lourd": "driving-hgv",
    "convoi_exceptionnel": "driving-hgv",
}

GRAPHOPPER_VEHICLES = {
    "pieton": "foot",
    "velo": "bike",
    "voiture": "car",
    "4x4": "car",
    "camping_car": "car",
    "poids_lourd": "car",
    "convoi_exceptionnel": "car",
}

FERRY_ROUTES = [
    {"nom": "Calais - Douvres", "depart": [50.966, 1.862], "arrivee": [51.127, 1.313], "duree_min": 90, "prix_eur": 180},
    {"nom": "Barcelone - Tanger Med", "depart": [41.34, 2.17], "arrivee": [35.88, -5.5], "duree_min": 900, "prix_eur": 350},
    {"nom": "Algeciras - Tanger Med", "depart": [36.13, -5.45], "arrivee": [35.88, -5.5], "duree_min": 90, "prix_eur": 150},
    {"nom": "Gênes - Palerme", "depart": [44.41, 8.93], "arrivee": [38.12, 13.36], "duree_min": 1200, "prix_eur": 300},
]


def liaisons_ferry():
    return FERRY_ROUTES


def _read_env_value(env_path, key_name):
    if not os.path.isfile(env_path):
        return None
    with open(env_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            candidate_key, candidate_value = line.split("=", 1)
            if candidate_key.strip() == key_name:
                return candidate_value.strip()
    return None


def _ors_api_key():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clé.env")
    load_dotenv(env_path)
    api_key = os.getenv("ORS_API_KEY")
    if not api_key:
        api_key = _read_env_value(env_path, "ORS_API_KEY")
    if not api_key:
        return None
    placeholder_markers = ("VOTRE_", "YOUR_", "CHANGE_ME", "changeme", "example")
    if api_key.upper().startswith(placeholder_markers):
        logger.warning("Clé ORS non configurée ou placeholder détectée; géocodage désactivé.")
        return None
    return api_key


def _ors_client():
    if openrouteservice is None:
        return None

    api_key = _ors_api_key()
    if not api_key:
        return None
    return openrouteservice.Client(key=api_key, base_url="https://api.heigit.org/openrouteservice")


def _graphhopper_api_key():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clé.env")
    load_dotenv(env_path)
    api_key = os.getenv("GRAPHOPPER_API_KEY") or _read_env_value(env_path, "GRAPHOPPER_API_KEY")
    if not api_key or api_key.upper().startswith(("VOTRE_", "YOUR_", "CHANGE_ME", "EXAMPLE", "REMPLACEZ_")):
        return None
    return api_key


def _graphhopper_route(lat1, lon1, lat2, lon2, profil):
    api_key = _graphhopper_api_key()
    if api_key is None:
        return None

    query = urllib.parse.urlencode(
        [
            ("point", f"{lat1},{lon1}"),
            ("point", f"{lat2},{lon2}"),
            ("vehicle", GRAPHOPPER_VEHICLES.get(profil, "car")),
            ("locale", "fr"),
            ("instructions", "true"),
            ("points_encoded", "false"),
            ("key", api_key),
        ]
    )
    url = f"https://graphhopper.com/api/1/route?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "Itineraire-C25/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    paths = payload.get("paths", [])
    if not paths:
        raise RuntimeError("GraphHopper ne propose pas de route")
    selected = paths[0]
    return {
        "distance_km": round(selected["distance"] / 1000, 2),
        "duree_min": round(selected["time"] / 60000, 1),
        "source": "graphhopper",
        "profil_ors": GRAPHOPPER_VEHICLES.get(profil, "car"),
        "steps": [
            {
                "instruction": instruction.get("text", "Continuer"),
                "distance_km": round(instruction.get("distance", 0) / 1000, 2),
                "duree_min": round(instruction.get("time", 0) / 60000, 1),
            }
            for instruction in selected.get("instructions", [])
        ],
        "geometry": selected["points"],
    }

def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en kilomètres entre deux points GPS.
    Formule de Haversine.
    """
    R = 6371  # Rayon de la Terre en km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def duree_minutes(distance_km: float, vitesse_kmh: float = 70) -> float:
    """
    Calcule la durée estimée en minutes.
    Par défaut : 70 km/h (camping-car C25).
    """
    if vitesse_kmh <= 0:
        return 0
    heures = distance_km / vitesse_kmh
    return heures * 60


def _osrm_route(lat1, lon1, lat2, lon2):
    coordinates = f"{lon1},{lat1};{lon2},{lat2}"
    query = urllib.parse.urlencode({"overview": "full", "geometries": "geojson", "steps": "true"})
    url = f"https://router.project-osrm.org/route/v1/driving/{coordinates}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "Itineraire-C25/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        route = json.loads(response.read().decode("utf-8"))
    if route.get("code") != "Ok" or not route.get("routes"):
        raise RuntimeError("OSRM ne propose pas de route")
    selected = route["routes"][0]
    steps = [
        {
            "instruction": step.get("name") or step.get("maneuver", {}).get("type", "Continuer"),
            "distance_km": round(step.get("distance", 0) / 1000, 2),
            "duree_min": round(step.get("duration", 0) / 60, 1),
        }
        for leg in selected.get("legs", [])
        for step in leg.get("steps", [])
    ]
    return {
        "distance_km": round(selected["distance"] / 1000, 2),
        "duree_min": round(selected["duration"] / 60, 1),
        "source": "osrm_fallback",
        "profil_ors": "driving-car",
        "steps": steps,
        "geometry": selected["geometry"],
    }


def _route_routiere(client, start, end, profile):
    route = client.directions(
        [[start[1], start[0]], [end[1], end[0]]],
        profile=profile,
        format="geojson",
    )
    feature = route["features"][0]
    summary = feature["properties"]["summary"]
    steps = []
    for segment in feature["properties"].get("segments", []):
        for step in segment.get("steps", []):
            steps.append({
                "instruction": step.get("instruction", ""),
                "distance_km": round(step.get("distance", 0) / 1000, 2),
                "duree_min": round(step.get("duration", 0) / 60, 1),
            })
    return summary, feature["geometry"], steps


def geocoder(adresse):
    api_key = _ors_api_key()
    if api_key is None:
        return []
    try:
        query = urllib.parse.urlencode({"text": adresse})
        request = urllib.request.Request(
            f"https://api.heigit.org/pelias/v1/search?{query}",
            headers={"Authorization": api_key, "User-Agent": "Itineraire-C25/1.0"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            response = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        logger.warning("Geocodage ORS indisponible: %s", error)
        return []
    return [
        {
            "nom": feature.get("properties", {}).get("label", adresse),
            "pays": feature.get("properties", {}).get("country"),
            "longitude": feature["geometry"]["coordinates"][0],
            "latitude": feature["geometry"]["coordinates"][1],
        }
        for feature in response.get("features", [])[:5]
    ]


def calcul_itineraire_avec_ferry(lat1, lon1, lat2, lon2, vitesse_kmh, profil):
    client = _ors_client()
    ors_profile = ORS_PROFILES.get(profil, "driving-car")
    if client is None:
        return None

    candidats = []
    for ferry in FERRY_ROUTES:
        try:
            depart_summary, depart_geometry, depart_steps = _route_routiere(client, (lat1, lon1), ferry["depart"], ors_profile)
            arrivee_summary, arrivee_geometry, arrivee_steps = _route_routiere(client, ferry["arrivee"], (lat2, lon2), ors_profile)
            total = depart_summary["duration"] + ferry["duree_min"] * 60 + arrivee_summary["duration"]
            candidats.append((total, ferry, depart_summary, depart_geometry, depart_steps, arrivee_summary, arrivee_geometry, arrivee_steps))
        except Exception as error:
            logger.info("Liaison ferry indisponible (%s): %s", ferry["nom"], error)

    if not candidats:
        return None

    _, ferry, depart_summary, depart_geometry, depart_steps, arrivee_summary, arrivee_geometry, arrivee_steps = min(candidats, key=lambda item: item[0])
    ferry_distance = distance_km(
        ferry["depart"][0], ferry["depart"][1],
        ferry["arrivee"][0], ferry["arrivee"][1],
    )
    coordinates = depart_geometry["coordinates"] + [ferry["depart"][::-1], ferry["arrivee"][::-1]] + arrivee_geometry["coordinates"]
    return {
        "distance_km": round((depart_summary["distance"] + arrivee_summary["distance"]) / 1000 + ferry_distance, 2),
        "duree_min": round((depart_summary["duration"] + arrivee_summary["duration"]) / 60 + ferry["duree_min"], 1),
        "vitesse_kmh": vitesse_kmh,
        "source": "openrouteservice_ferry",
        "profil_ors": ors_profile,
        "ferry": ferry,
        "steps": depart_steps + [{"instruction": f"Embarquer : {ferry['nom']}", "distance_km": round(ferry_distance, 2), "duree_min": ferry["duree_min"]}] + arrivee_steps,
        "geometry": {"type": "LineString", "coordinates": coordinates},
    }


def calcul_itineraire(
    lat1,
    lon1,
    lat2,
    lon2,
    vitesse_kmh=70,
    profil="camping_car",
    contraintes=None,
):
    """
    Retourne un itinéraire GraphHopper, ORS ou un calcul de secours local.
    """
    try:
        graphhopper_route = _graphhopper_route(lat1, lon1, lat2, lon2, profil)
        if graphhopper_route is not None:
            graphhopper_route["vitesse_kmh"] = vitesse_kmh
            return graphhopper_route
    except Exception as error:
        logger.warning("Routage GraphHopper indisponible, fallback ORS: %s", error)

    client = _ors_client()
    ors_profile = ORS_PROFILES.get(profil, "driving-car")

    if client is not None:
        try:
            route = client.directions(
                [[lon1, lat1], [lon2, lat2]],
                profile=ors_profile,
                format="geojson",
            )
            feature = route["features"][0]
            summary = feature["properties"]["summary"]
            steps = []
            for segment in feature["properties"].get("segments", []):
                for step in segment.get("steps", []):
                    steps.append({
                        "instruction": step.get("instruction", ""),
                        "distance_km": round(step.get("distance", 0) / 1000, 2),
                        "duree_min": round(step.get("duration", 0) / 60, 1),
                    })
            return {
                "distance_km": round(summary["distance"] / 1000, 2),
                "duree_min": round(summary["duration"] / 60, 1),
                "vitesse_kmh": vitesse_kmh,
                "source": "openrouteservice",
                "profil_ors": ors_profile,
                "steps": steps,
                "geometry": feature["geometry"],
            }
        except Exception as error:
            logger.warning("Routage ORS indisponible, fallback local: %s", error)

    try:
        fallback = _osrm_route(lat1, lon1, lat2, lon2)
        fallback["vitesse_kmh"] = vitesse_kmh
        return fallback
    except Exception as error:
        logger.warning("Routage OSRM indisponible, fallback Haversine: %s", error)

    dist = distance_km(lat1, lon1, lat2, lon2)
    duree = duree_minutes(dist, vitesse_kmh)
    return {
        "distance_km": round(dist, 2),
        "duree_min": round(duree, 1),
        "vitesse_kmh": vitesse_kmh,
        "source": "haversine_fallback",
        "profil_ors": ors_profile,
        "geometry": {
            "type": "LineString",
            "coordinates": [[lon1, lat1], [lon2, lat2]],
        },
    }
