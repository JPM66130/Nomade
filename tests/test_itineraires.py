from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_itineraires():
    response = client.get("/itineraires")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_itineraire_by_id():
    response = client.get("/itineraires/1")
    assert response.status_code == 200
    assert "distance" in response.json()
