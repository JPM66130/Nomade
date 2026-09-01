from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_spots():
    response = client.get("/spots")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_spot_by_id():
    response = client.get("/spots/1")
    assert response.status_code == 200
    assert "nom" in response.json()
