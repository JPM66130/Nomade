from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from db import get_db
from models.itineraires import Itineraire
from utils.geo import calcul_itineraire, calcul_itineraire_avec_ferry, geocoder, liaisons_ferry
from utils.carburants import get_eu_fuel_prices, get_fuel_prices

router = APIRouter(prefix="/itineraire", tags=["Itinéraires"])

VehicleProfile = Literal[
    "pieton",
    "velo",
    "voiture",
    "4x4",
    "camping_car",
    "poids_lourd",
    "convoi_exceptionnel",
]

VEHICLE_PROFILES = {
    "pieton": {
        "libelle": "Piéton",
        "vitesse_max_kmh": 6,
        "hauteur_m": 0.0,
        "largeur_m": 0.6,
        "longueur_m": 0.6,
        "poids_max_t": 0.0,
        "consommation_l_100": 0.0,
    },
    "velo": {
        "libelle": "Vélo",
        "vitesse_max_kmh": 35,
        "hauteur_m": 0.0,
        "largeur_m": 0.8,
        "longueur_m": 1.9,
        "poids_max_t": 0.15,
        "consommation_l_100": 0.0,
    },
    "voiture": {
        "libelle": "Voiture",
        "vitesse_max_kmh": 130,
        "hauteur_m": 2.0,
        "largeur_m": 2.0,
        "longueur_m": 5.0,
        "poids_max_t": 3.5,
        "consommation_l_100": 7.0,
    },
    "4x4": {
        "libelle": "4x4",
        "vitesse_max_kmh": 110,
        "hauteur_m": 2.4,
        "largeur_m": 2.2,
        "longueur_m": 5.5,
        "poids_max_t": 3.5,
        "consommation_l_100": 9.0,
    },
    "camping_car": {
        "libelle": "Camping-car",
        "vitesse_max_kmh": 100,
        "hauteur_m": 3.2,
        "largeur_m": 2.5,
        "longueur_m": 9.0,
        "poids_max_t": 7.5,
        "consommation_l_100": 10.0,
    },
    "poids_lourd": {
        "libelle": "Poids lourd",
        "vitesse_max_kmh": 90,
        "hauteur_m": 4.0,
        "largeur_m": 2.6,
        "longueur_m": 18.75,
        "poids_max_t": 44.0,
        "consommation_l_100": 28.0,
    },
    "convoi_exceptionnel": {
        "libelle": "Convoi exceptionnel",
        "vitesse_max_kmh": 80,
        "hauteur_m": 5.0,
        "largeur_m": 4.0,
        "longueur_m": 30.0,
        "poids_max_t": 100.0,
        "consommation_l_100": 35.0,
    },
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
    taux_peage = {"pieton": 0.0, "velo": 0.0, "voiture": 0.09, "4x4": 0.11, "camping_car": 0.12, "poids_lourd": 0.22, "convoi_exceptionnel": 0.28}[profil]
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
    db.commit()
    db.refresh(itin)

    carburant_eur = round(result["distance_km"] * consommation * prix_carburant / 100, 2)
    peages_eur = round(result["distance_km"] * taux_peage, 2)
    ferry_eur = result.get("ferry", {}).get("prix_eur", 0)
    avertissements_routage = []
    if profil in {"camping_car", "poids_lourd", "convoi_exceptionnel"}:
        avertissements_routage.append(
            "Les contraintes de hauteur, largeur, longueur et poids sont informatives et ne sont pas garanties par le moteur de routage."
        )

    return {
        "itineraire_id": itin.id,
        "distance_km": itin.distance_km,
        "duree_min": itin.duree_min,
        "vitesse_kmh": vitesse_retenue,
        "profil": profil,
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


@router.get("/")
def liste_itineraires(db: Session = Depends(get_db)):
    return db.query(Itineraire).all()


