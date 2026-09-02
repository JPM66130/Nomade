from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_pays():
    response = client.get("/pays")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_get_pays_by_id():
    response = client.get("/pays/1")
    assert response.status_code == 200
    assert response.json()["nom"] == "France"
