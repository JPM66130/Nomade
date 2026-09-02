from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# --- 404 NOT FOUND ---

def test_station_not_found():
    response = client.get("/stations/9999")
    assert response.status_code == 404

def test_spot_not_found():
    response = client.get("/spots/9999")
    assert response.status_code == 404

def test_parking_not_found():
    response = client.get("/parkings/9999")
    assert response.status_code == 404

def test_alerte_not_found():
    response = client.get("/alertes/9999")
    assert response.status_code == 404

def test_itineraire_not_found():
    response = client.get("/itineraires/9999")
    assert response.status_code == 404


# --- 422 UNPROCESSABLE ENTITY (invalid values) ---

def test_invalid_station_id():
    response = client.get("/stations/abc")
    assert response.status_code == 422

def test_invalid_spot_id():
    response = client.get("/spots/abc")
    assert response.status_code == 422

def test_invalid_parking_id():
    response = client.get("/parkings/abc")
    assert response.status_code == 422

def test_invalid_alerte_id():
    response = client.get("/alertes/abc")
    assert response.status_code == 422

def test_invalid_itineraire_id():
    response = client.get("/itineraires/abc")
    assert response.status_code == 422
