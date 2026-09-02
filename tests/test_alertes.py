from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_alertes():
    response = client.get("/alertes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_alerte_by_id():
    response = client.get("/alertes/1")
    assert response.status_code == 200
    assert "type" in response.json()
