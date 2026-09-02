from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_stations():
    response = client.get("/stations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_station_by_id():
    response = client.get("/stations/1")
    assert response.status_code == 200
    assert "nom" in response.json()
