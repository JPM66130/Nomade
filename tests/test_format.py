from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# --- FORMAT STATIONS ---

def test_format_station():
    response = client.get("/stations/1")
    assert response.status_code == 200
    data = response.json()
    assert "nom" in data
    assert "ville" in data
    assert "coord" in data


# --- FORMAT SPOTS ---

def test_format_spot():
    response = client.get("/spots/1")
    assert response.status_code == 200
    data = response.json()
    assert "nom" in data
    assert "type" in data
    assert "coord" in data


# --- FORMAT PARKINGS ---

def test_format_parking():
    response = client.get("/parkings/1")
    assert response.status_code == 200
    data = response.json()
    assert "nom" in data
    assert "places" in data
    assert "gratuit" in data


# --- FORMAT ALERTES ---

def test_format_alerte():
    response = client.get("/alertes/1")
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "message" in data


# --- FORMAT ITINERAIRES ---

def test_format_itineraire():
    response = client.get("/itineraires/1")
    assert response.status_code == 200
    data = response.json()
    assert "distance" in data
    assert "depart" in data
    assert "arrivee" in data
