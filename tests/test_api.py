import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import main
import routers.itineraires as itineraires_router
from db import Base, get_db


class ItineraireApiTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db():
            db = session_factory()
            try:
                yield db
            finally:
                db.close()

        main.app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(main.app, client=("127.0.0.1", 50000))
        self.engine = engine

    def tearDown(self):
        main.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_profils_exposes_vehicle_limits(self):
        response = self.client.get("/itineraire/profils")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"voiture", "bus"})
        self.assertEqual(response.json()["bus"]["hauteur_m"], 4.0)

    def test_calcul_persists_and_returns_route_contract(self):
        route = {
            "distance_km": 12.5,
            "duree_min": 18.0,
            "source": "graphhopper",
            "profil_ors": "car",
            "steps": [],
            "geometry": {"type": "LineString", "coordinates": [[2.621, 42.668], [2.395, 42.55]]},
        }

        with patch.object(itineraires_router, "calcul_itineraire", return_value=route):
            response = self.client.get(
                "/itineraire/calcul",
                params={
                    "lat1": 42.668,
                    "lon1": 2.621,
                    "lat2": 42.55,
                    "lon2": 2.395,
                    "vitesse": 70,
                    "profil": "voiture",
                },
            )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["source_routage"], "graphhopper")
        self.assertEqual(body["distance_km"], 12.5)
        self.assertEqual(body["estimation_cout"]["carburant_eur"], 1.62)
        self.assertEqual(body["avertissements_routage"], [])
        self.assertIsInstance(body["itineraire_id"], int)

        history = self.client.get("/itineraire/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json()), 1)
        self.assertEqual(history.json()[0]["id"], body["itineraire_id"])
        self.assertEqual(history.json()[0]["nom_tournee"], "Tournée sans nom")

        update_response = self.client.put(
            f"/itineraire/{body['itineraire_id']}/tournee",
            json={"nom_tournee": "Ligne gare - centre-ville"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["nom_tournee"], "Ligne gare - centre-ville")
        self.assertEqual(self.client.get("/itineraire/").json()[0]["nom_tournee"], "Ligne gare - centre-ville")

    def test_bus_stop_is_saved_with_its_position_and_direction(self):
        route = {
            "distance_km": 12.5,
            "duree_min": 18.0,
            "source": "graphhopper",
            "profil_ors": "car",
            "steps": [],
            "geometry": {"type": "LineString", "coordinates": [[2.621, 42.668], [2.395, 42.55]]},
        }
        with patch.object(itineraires_router, "calcul_itineraire", return_value=route):
            trip_response = self.client.get(
                "/itineraire/calcul",
                params={"lat1": 42.668, "lon1": 2.621, "lat2": 42.55, "lon2": 2.395, "profil": "bus"},
            )

        stop_response = self.client.post(
            f"/itineraire/{trip_response.json()['itineraire_id']}/arrets",
            json={"nom": "Gare centrale", "latitude": 42.66, "longitude": 2.5, "direction_deg": 213.5, "precision_m": 4.0},
        )

        self.assertEqual(stop_response.status_code, 200)
        self.assertEqual(stop_response.json()["nom"], "Gare centrale")
        self.assertEqual(stop_response.json()["direction_deg"], 213.5)
        history = self.client.get("/itineraire/").json()
        self.assertEqual(history[0]["profil"], "bus")
        self.assertEqual(history[0]["arrets"][0]["latitude"], 42.66)

        for index in range(19):
            response = self.client.post(
                f"/itineraire/{trip_response.json()['itineraire_id']}/arrets",
                json={"nom": f"Arrêt {index + 2}", "latitude": 42.66, "longitude": 2.5, "direction_deg": 213.5, "precision_m": 4.0},
            )
            self.assertEqual(response.status_code, 200)
        limit_response = self.client.post(
            f"/itineraire/{trip_response.json()['itineraire_id']}/arrets",
            json={"nom": "Arrêt 21", "latitude": 42.66, "longitude": 2.5, "direction_deg": 213.5, "precision_m": 4.0},
        )
        self.assertEqual(limit_response.status_code, 409)

    def test_history_keeps_only_the_twenty_most_recent_trips(self):
        route = {
            "distance_km": 12.5,
            "duree_min": 18.0,
            "source": "graphhopper",
            "profil_ors": "car",
            "steps": [],
            "geometry": {"type": "LineString", "coordinates": [[2.621, 42.668], [2.395, 42.55]]},
        }
        trip_ids = []
        with patch.object(itineraires_router, "calcul_itineraire", return_value=route):
            for _ in range(21):
                response = self.client.get(
                    "/itineraire/calcul",
                    params={"lat1": 42.668, "lon1": 2.621, "lat2": 42.55, "lon2": 2.395, "profil": "voiture"},
                )
                self.assertEqual(response.status_code, 200)
                trip_ids.append(response.json()["itineraire_id"])

        history = self.client.get("/itineraire/").json()
        self.assertEqual(len(history), 20)
        self.assertNotIn(trip_ids[0], [trip["id"] for trip in history])

    def test_calcul_rejects_an_invalid_speed_before_routing(self):
        response = self.client.get(
            "/itineraire/calcul",
            params={
                "lat1": 42.668,
                "lon1": 2.621,
                "lat2": 42.55,
                "lon2": 2.395,
                "vitesse": 0,
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_external_requests_are_rate_limited(self):
        original_token = main.API_ACCESS_TOKEN
        original_limit = main.RATE_LIMIT_PER_MINUTE
        main.API_ACCESS_TOKEN = None
        main.RATE_LIMIT_PER_MINUTE = 1
        main.request_times.clear()
        try:
            external_client = TestClient(main.app)
            first_response = external_client.get("/itineraire/profils")
            second_response = external_client.get("/itineraire/profils")

            self.assertEqual(first_response.status_code, 200)
            self.assertEqual(second_response.status_code, 429)
        finally:
            main.API_ACCESS_TOKEN = original_token
            main.RATE_LIMIT_PER_MINUTE = original_limit
            main.request_times.clear()


if __name__ == "__main__":
    unittest.main()