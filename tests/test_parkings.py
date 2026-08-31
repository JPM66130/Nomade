from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_parkings():
    response = client.get("/parkings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_parking_by_id():
    response = client.get("/parkings/1")
    assert response.status_code == 200
    assert "nom" in response.json()
