from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_shipment_count():
    response = client.get("/shipments/count")

    assert response.status_code == 200

    data = response.json()

    assert "total_shipments" in data
    assert data["total_shipments"] == 172765


def test_shipments_endpoint():
    response = client.get("/shipments?limit=5&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert "shipments" in data
    assert len(data["shipments"]) == 5


def test_shipment_search():
    response = client.get("/shipments/search?q=CA&limit=5")

    assert response.status_code == 200

    data = response.json()

    assert "shipments" in data
