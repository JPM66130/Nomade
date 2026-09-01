import os
import tempfile
import unittest
from pathlib import Path

import utils.geo as geo


class FakeClient:
    def directions(self, *args, **kwargs):
        return {
            "features": [
                {
                    "properties": {
                        "summary": {"distance": 2500, "duration": 600},
                        "segments": [
                            {
                                "steps": [
                                    {"instruction": "go", "distance": 100, "duration": 10}
                                ]
                            }
                        ],
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[2.621, 42.668], [2.395, 42.55]],
                    },
                }
            ]
        }


class GeoCalculTest(unittest.TestCase):
    def test_graphhopper_uses_foot_vehicle_for_pedestrian_profile(self):
        original_api_key = geo._graphhopper_api_key
        original_urlopen = geo.urllib.request.urlopen

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"paths":[{"distance":300,"time":240000,"instructions":[],"points":{"type":"LineString","coordinates":[[2.3,48.8],[2.31,48.81]]}}]}'

        def fake_urlopen(request, timeout):
            self.assertIn("vehicle=foot", request.full_url)
            return FakeResponse()

        geo._graphhopper_api_key = lambda: "test-key"
        geo.urllib.request.urlopen = fake_urlopen
        try:
            result = geo._graphhopper_route(48.8, 2.3, 48.81, 2.31, "pieton")
            self.assertEqual(result["profil_ors"], "foot")
        finally:
            geo._graphhopper_api_key = original_api_key
            geo.urllib.request.urlopen = original_urlopen

    def test_calcul_itineraire_graphhopper(self):
        original_graphhopper_route = geo._graphhopper_route
        geo._graphhopper_route = lambda *args: {
            "distance_km": 2.5,
            "duree_min": 10.0,
            "source": "graphhopper",
            "profil_ors": "car",
            "steps": [{"instruction": "Continuer", "distance_km": 2.5, "duree_min": 10.0}],
            "geometry": {"type": "LineString", "coordinates": [[2.621, 42.668], [2.395, 42.55]]},
        }
        try:
            result = geo.calcul_itineraire(42.668, 2.621, 42.55, 2.395, 70, "camping_car", None)
            self.assertEqual(result["source"], "graphhopper")
            self.assertEqual(result["vitesse_kmh"], 70)
            self.assertIn("steps", result)
        finally:
            geo._graphhopper_route = original_graphhopper_route

    def test_calcul_itineraire_ors(self):
        original_graphhopper_route = geo._graphhopper_route
        original_client = geo._ors_client
        geo._graphhopper_route = lambda *args: None
        geo._ors_client = lambda: FakeClient()
        try:
            result = geo.calcul_itineraire(42.668, 2.621, 42.55, 2.395, 70, "camping_car", None)
            self.assertEqual(result["source"], "openrouteservice")
            self.assertIn("steps", result)
            self.assertGreater(len(result["steps"]), 0)
        finally:
            geo._graphhopper_route = original_graphhopper_route
            geo._ors_client = original_client

    def test_calcul_itineraire_falls_back_to_ors_when_graphhopper_fails(self):
        original_graphhopper_route = geo._graphhopper_route
        original_client = geo._ors_client

        def graphhopper_failure(*args):
            raise RuntimeError("GraphHopper indisponible")

        geo._graphhopper_route = graphhopper_failure
        geo._ors_client = lambda: FakeClient()
        try:
            result = geo.calcul_itineraire(42.668, 2.621, 42.55, 2.395, 70, "camping_car", None)
            self.assertEqual(result["source"], "openrouteservice")
        finally:
            geo._graphhopper_route = original_graphhopper_route
            geo._ors_client = original_client

    def test_calcul_itineraire_falls_back_to_osrm_when_ors_is_unavailable(self):
        original_graphhopper_route = geo._graphhopper_route
        original_client = geo._ors_client
        original_osrm_route = geo._osrm_route
        osrm_result = {
            "distance_km": 3.1,
            "duree_min": 8.0,
            "source": "osrm_fallback",
            "profil_ors": "driving-car",
            "steps": [],
            "geometry": {"type": "LineString", "coordinates": [[2.621, 42.668], [2.395, 42.55]]},
        }

        geo._graphhopper_route = lambda *args: None
        geo._ors_client = lambda: None
        geo._osrm_route = lambda *args: osrm_result.copy()
        try:
            result = geo.calcul_itineraire(42.668, 2.621, 42.55, 2.395, 70, "camping_car", None)
            self.assertEqual(result["source"], "osrm_fallback")
            self.assertEqual(result["vitesse_kmh"], 70)
        finally:
            geo._graphhopper_route = original_graphhopper_route
            geo._ors_client = original_client
            geo._osrm_route = original_osrm_route

    def test_calcul_itineraire_falls_back_to_osrm_when_ors_fails(self):
        original_graphhopper_route = geo._graphhopper_route
        original_client = geo._ors_client
        original_osrm_route = geo._osrm_route

        class FailingClient:
            def directions(self, *args, **kwargs):
                raise RuntimeError("ORS indisponible")

        geo._graphhopper_route = lambda *args: None
        geo._ors_client = lambda: FailingClient()
        geo._osrm_route = lambda *args: {
            "distance_km": 3.1,
            "duree_min": 8.0,
            "source": "osrm_fallback",
            "profil_ors": "driving-car",
            "steps": [],
            "geometry": {"type": "LineString", "coordinates": [[2.621, 42.668], [2.395, 42.55]]},
        }
        try:
            result = geo.calcul_itineraire(42.668, 2.621, 42.55, 2.395, 70, "camping_car", None)
            self.assertEqual(result["source"], "osrm_fallback")
        finally:
            geo._graphhopper_route = original_graphhopper_route
            geo._ors_client = original_client
            geo._osrm_route = original_osrm_route

    def test_calcul_itineraire_uses_haversine_when_all_engines_fail(self):
        original_graphhopper_route = geo._graphhopper_route
        original_client = geo._ors_client
        original_osrm_route = geo._osrm_route

        def osrm_failure(*args):
            raise RuntimeError("OSRM indisponible")

        geo._graphhopper_route = lambda *args: None
        geo._ors_client = lambda: None
        geo._osrm_route = osrm_failure
        try:
            result = geo.calcul_itineraire(42.668, 2.621, 42.55, 2.395, 70, "camping_car", None)
            self.assertEqual(result["source"], "haversine_fallback")
            self.assertGreater(result["distance_km"], 0)
            self.assertGreater(result["duree_min"], 0)
        finally:
            geo._graphhopper_route = original_graphhopper_route
            geo._ors_client = original_client
            geo._osrm_route = original_osrm_route

    def test_ors_client_rejects_placeholder(self):
        original_env = os.environ.get("ORS_API_KEY")
        try:
            os.environ["ORS_API_KEY"] = "VOTRE_CLE_ORS"
            self.assertIsNone(geo._ors_client())
        finally:
            if original_env is None:
                os.environ.pop("ORS_API_KEY", None)
            else:
                os.environ["ORS_API_KEY"] = original_env

    def test_read_env_value_ignores_unrelated_lines(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / "clé.env"
            env_path.write_text("ORS_API_KEY=VOTRE_CLE_ORS\n" + "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImU0YjU1YTU3MGQxNTQ4OTc4Njk1NWFjMTE2ODg0OGY2IiwiaCI6Im11cm11cjY0In0=\nAPI_ACCESS_TOKEN=abc\n", encoding="utf-8")
            self.assertEqual(geo._read_env_value(str(env_path), "ORS_API_KEY"), "VOTRE_CLE_ORS")


if __name__ == "__main__":
    unittest.main()
