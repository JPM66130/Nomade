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
        self.assertEqual(response.json()["camping_car"]["hauteur_m"], 3.2)
        self.assertEqual(response.json()["pieton"]["consommation_l_100"], 0.0)

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
                    "profil": "camping_car",
                },
            )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["source_routage"], "graphhopper")
        self.assertEqual(body["distance_km"], 12.5)
        self.assertEqual(body["estimation_cout"]["carburant_eur"], 2.31)
        self.assertEqual(len(body["avertissements_routage"]), 1)
        self.assertIsInstance(body["itineraire_id"], int)

        history = self.client.get("/itineraire/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json()), 1)
        self.assertEqual(history.json()[0]["id"], body["itineraire_id"])

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