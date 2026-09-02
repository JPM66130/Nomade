from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# --- FILTRES STATIONS ---

def test_filter_stations_ville():
    response = client.get("/stations?ville=Paris")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for station in data:
        assert station.get("ville") == "Paris"


# --- FILTRES SPOTS ---

def test_filter_spots_type():
    response = client.get("/spots?type=camping")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for spot in data:
        assert spot.get("type") == "camping"


# --- FILTRES PARKINGS ---

def test_filter_parkings_gratuit():
    response = client.get("/parkings?gratuit=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for parking in data:
        assert parking.get("gratuit") is True


# --- FILTRES ITINERAIRES ---

def test_filter_itineraires_max_distance():
    response = client.get("/itineraires?max_distance=50")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for iti in data:
        assert iti.get("distance") <= 50
