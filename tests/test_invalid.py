from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# --- INVALID ID TYPES ---

def test_invalid_station_id_type():
    response = client.get("/stations?id=abc")
    assert response.status_code in (400, 422)

def test_invalid_spot_id_type():
    response = client.get("/spots?id=abc")
    assert response.status_code in (400, 422)

def test_invalid_parking_id_type():
    response = client.get("/parkings?id=abc")
    assert response.status_code in (400, 422)


# --- NEGATIVE VALUES ---

def test_negative_station_id():
    response = client.get("/stations/-1")
    assert response.status_code in (400, 422)

def test_negative_spot_id():
    response = client.get("/spots/-1")
    assert response.status_code in (400, 422)

def test_negative_parking_id():
    response = client.get("/parkings/-1")
    assert response.status_code in (400, 422)


# --- EMPTY PARAMETERS ---

def test_empty_spot_type():
    response = client.get("/spots?type=")
    assert response.status_code in (400, 422)

def test_empty_station_ville():
    response = client.get("/stations?ville=")
    assert response.status_code in (400, 422)


# --- INVALID BOOLEAN ---

def test_invalid_parking_gratuit():
    response = client.get("/parkings?gratuit=maybe")
    assert response.status_code in (400, 422)


# --- INVALID NUMERIC FILTERS ---

def test_invalid_itineraire_max_distance():
    response = client.get("/itineraires?max_distance=abc")
    assert response.status_code in (400, 422)

def test_negative_itineraire_max_distance():
    response = client.get("/itineraires?max_distance=-10")
    assert response.status_code in (400, 422)
