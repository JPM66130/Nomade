import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# --- PERFORMANCE STATIONS ---

def test_performance_stations():
    start = time.time()
    response = client.get("/stations")
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 0.5  # 500 ms max


# --- PERFORMANCE SPOTS ---

def test_performance_spots():
    start = time.time()
    response = client.get("/spots")
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 0.5


# --- PERFORMANCE PARKINGS ---

def test_performance_parkings():
    start = time.time()
    response = client.get("/parkings")
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 0.5


# --- PERFORMANCE ALERTES ---

def test_performance_alertes():
    start = time.time()
    response = client.get("/alertes")
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 0.5


# --- PERFORMANCE ITINERAIRES ---

def test_performance_itineraires():
    start = time.time()
    response = client.get("/itineraires")
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 0.5
