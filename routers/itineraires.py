import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from db import get_db
from models.arrets import Arret
from models.itineraires import Itineraire
from models.trajet_details import TrajetDetail
from utils.geo import calcul_itineraire, calcul_itineraire_avec_ferry, geocoder, liaisons_ferry
from utils.carburants import get_eu_fuel_prices, get_fuel_prices

router = APIRouter(prefix="/itineraire", tags=["Itinéraires"])

VehicleProfile = Literal[
    "voiture",
    "bus",
]

MAX_SAVED_TRIPS = 20
MAX_STOPS_PER_TRIP = 20


class ArretCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=80)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    direction_deg: float = Field(ge=0, lt=360)
    precision_m: float = Field(ge=0, le=100)


class TourneeUpdate(BaseModel):
    nom_tournee: str = Field(min_length=1, max_length=80)


VEHICLE_PROFILES = {
    "voiture": {
        "libelle": "Voiture",
        "vitesse_max_kmh": 130,
        "hauteur_m": 2.0,
        "largeur_m": 2.0,
        "longueur_m": 5.0,
        "poids_max_t": 3.5,
        "consommation_l_100": 7.0,
    },
    "bus": {
        "libelle": "Bus",
        "vitesse_max_kmh": 90,
        "hauteur_m": 4.0,
        "largeur_m": 2.6,
        "longueur_m": 18.0,
        "poids_max_t": 19.0,
        "consommation_l_100": 30.0,
    },
}


def _serialize_stop(stop):
    return {
        "id": stop.id,
        "nom": stop.nom,
        "latitude": stop.latitude,
        "longitude": stop.longitude,
        "direction_deg": stop.direction_deg,
        "precision_m": stop.precision_m,
    }


def _serialize_trip(itineraire, db):
    detail = db.query(TrajetDetail).filter(TrajetDetail.itineraire_id == itineraire.id).one_or_none()
    stops = db.query(Arret).filter(Arret.itineraire_id == itineraire.id).order_by(Arret.id).all()
    return {
        "id": itineraire.id,
        "depart": itineraire.depart,
        "arrivee": itineraire.arrivee,
        "lat_depart": itineraire.lat_depart,
        "lon_depart": itineraire.lon_depart,
        "lat_arrivee": itineraire.lat_arrivee,
        "lon_arrivee": itineraire.lon_arrivee,
        "distance_km": itineraire.distance_km,
        "duree_min": itineraire.duree_min,
        "profil": detail.profil if detail else "voiture",
        "nom_tournee": detail.nom_tournee if detail else "Tournée sans nom",
        "geometry": json.loads(detail.geometry_json) if detail else None,
        "arrets": [_serialize_stop(stop) for stop in stops],
    }


@router.get("/profils")
def liste_profils():
    return VEHICLE_PROFILES

@router.get("/ferries")
def liste_ferries():
    return liaisons_ferry()

@router.get("/geocoder")
def rechercher_adresse(adresse: str):
    return geocoder(adresse)

@router.get("/carburants")
def prix_carburants():
    return get_fuel_prices()

@router.get("/carburants-europe")
def prix_carburants_europe():
    return get_eu_fuel_prices()

@router.get("/calcul")
def calculer_itineraire(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    vitesse: float = Query(70, gt=0, le=130),
    profil: VehicleProfile = "camping_car",
    avec_ferry: bool = False,
    prix_carburant: float = Query(1.85, gt=0, le=10),
    consommation_l_100: float | None = Query(None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    profile_config = VEHICLE_PROFILES[profil]
    vitesse_retenue = min(vitesse, profile_config["vitesse_max_kmh"])
    consommation = consommation_l_100 if consommation_l_100 is not None else profile_config["consommation_l_100"]
    taux_peage = {"voiture": 0.09, "bus": 0.22}[profil]
    result = calcul_itineraire_avec_ferry(lat1, lon1, lat2, lon2, vitesse_retenue, profil) if avec_ferry else None
    if result is None:
        result = calcul_itineraire(lat1, lon1, lat2, lon2, vitesse_retenue, profil, profile_config)

    itin = Itineraire(
        depart=f"{lat1},{lon1}",
        arrivee=f"{lat2},{lon2}",
        lat_depart=lat1,
        lon_depart=lon1,
        lat_arrivee=lat2,
        lon_arrivee=lon2,
        distance_km=result["distance_km"],
        duree_min=result["duree_min"]
    )

    db.add(itin)
    db.flush()
    db.add(TrajetDetail(itineraire_id=itin.id, profil=profil, geometry_json=json.dumps(result["geometry"])))
    outdated_ids = [
        row[0]
        for row in db.query(Itineraire.id).order_by(Itineraire.id.desc()).offset(MAX_SAVED_TRIPS).all()
    ]
    if outdated_ids:
        db.query(Arret).filter(Arret.itineraire_id.in_(outdated_ids)).delete(synchronize_session=False)
        db.query(TrajetDetail).filter(TrajetDetail.itineraire_id.in_(outdated_ids)).delete(synchronize_session=False)
        db.query(Itineraire).filter(Itineraire.id.in_(outdated_ids)).delete(synchronize_session=False)
    db.commit()
    db.refresh(itin)

    carburant_eur = round(result["distance_km"] * consommation * prix_carburant / 100, 2)
    peages_eur = round(result["distance_km"] * taux_peage, 2)
    ferry_eur = result.get("ferry", {}).get("prix_eur", 0)
    avertissements_routage = []
    if profil == "bus":
        avertissements_routage.append(
            "Les contraintes propres au bus et les voies réservées ne sont pas garanties par le moteur de routage."
        )

    return {
        "itineraire_id": itin.id,
        "distance_km": itin.distance_km,
        "duree_min": itin.duree_min,
        "vitesse_kmh": vitesse_retenue,
        "profil": profil,
        "nom_tournee": "Tournée sans nom",
        "contraintes_vehicule": profile_config,
        "avertissements_routage": avertissements_routage,
        "source_routage": result["source"],
        "profil_ors": result["profil_ors"],
        "ferry": result.get("ferry"),
        "etapes": result.get("steps", []),
        "estimation_cout": {
            "carburant_l": round(result["distance_km"] * consommation / 100, 1),
            "prix_carburant_eur_l": prix_carburant,
            "consommation_l_100": consommation,
            "carburant_eur": carburant_eur,
            "peages_eur": peages_eur,
            "ferry_eur": ferry_eur,
            "total_eur": round(carburant_eur + peages_eur + ferry_eur, 2),
            "precision": "Estimations: péages au kilomètre selon le véhicule, ferry indicatif; hors horaires, promotions et recharge électrique.",
        },
        "geometry": result["geometry"],
    }


@router.get("/compteur")
def compteur_kilometrique(db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(Itineraire.distance_km), 0.0)).scalar()
    trajets = db.query(func.count(Itineraire.id)).scalar()
    return {
        "total_km": round(float(total), 2),
        "trajets": trajets,
    }


@router.post("/{itineraire_id}/arrets")
def marquer_arret(itineraire_id: int, payload: ArretCreate, db: Session = Depends(get_db)):
    itineraire = db.get(Itineraire, itineraire_id)
    if itineraire is None:
        raise HTTPException(status_code=404, detail="Itinéraire introuvable.")
    detail = db.query(TrajetDetail).filter(TrajetDetail.itineraire_id == itineraire_id).one_or_none()
    if detail is None or detail.profil != "bus":
        raise HTTPException(status_code=422, detail="Les arrêts peuvent uniquement être marqués sur un trajet bus.")
    if db.query(Arret).filter(Arret.itineraire_id == itineraire_id).count() >= MAX_STOPS_PER_TRIP:
        raise HTTPException(status_code=409, detail="Un trajet bus peut contenir au maximum 20 arrêts.")

    arret = Arret(itineraire_id=itineraire_id, **payload.model_dump())
    db.add(arret)
    db.commit()
    db.refresh(arret)
    return _serialize_stop(arret)


@router.put("/{itineraire_id}/tournee")
def nommer_tournee(itineraire_id: int, payload: TourneeUpdate, db: Session = Depends(get_db)):
    detail = db.query(TrajetDetail).filter(TrajetDetail.itineraire_id == itineraire_id).one_or_none()
    if detail is None:
        raise HTTPException(status_code=404, detail="Itinéraire introuvable.")
    detail.nom_tournee = payload.nom_tournee.strip()
    db.commit()
    return {"itineraire_id": itineraire_id, "nom_tournee": detail.nom_tournee}


@router.get("/")
def liste_itineraires(db: Session = Depends(get_db)):
    itineraires = db.query(Itineraire).order_by(Itineraire.id.desc()).limit(MAX_SAVED_TRIPS).all()
    return [_serialize_trip(itineraire, db) for itineraire in itineraires]


