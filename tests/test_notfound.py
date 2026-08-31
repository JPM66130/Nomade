from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# --- ROUTES INEXISTANTES ---

def test_route_inexistante_simple():
    response = client.get("/ceci-n-existe-pas")
    assert response.status_code == 404

def test_route_inexistante_sous_dossier():
    response = client.get("/stations/abc/def")
    assert response.status_code == 404

def test_route_inexistante_post():
    response = client.post("/route-inexistante")
    assert response.status_code == 404

def test_route_inexistante_put():
    response = client.put("/route-inexistante")
    assert response.status_code == 404

def test_route_inexistante_delete():
    response = client.delete("/route-inexistante")
    assert response.status_code == 404
