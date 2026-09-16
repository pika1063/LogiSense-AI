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
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_shipments_pagination():
    r1 = client.get("/shipments?limit=3&offset=0")
    r2 = client.get("/shipments?limit=3&offset=3")
    assert r1.status_code == 200
    assert r2.status_code == 200
    data1 = r1.json()["shipments"]
    data2 = r2.json()["shipments"]
    assert len(data1) == 3
    assert len(data2) == 3
    # Check that different offsets yield different records
    assert data1[0] != data2[0]


def test_shipment_search_query():
    response = client.get("/shipments/search?q=Cleats&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "shipments" in data
    assert len(data["shipments"]) <= 5


def test_shipment_search_structured():
    response = client.get(
        "/shipments/search?shipping_mode=Standard%20Class&market=LATAM&late_delivery_risk=1&limit=5"
    )
    assert response.status_code == 200
    data = response.json()
    assert "shipments" in data
    for item in data["shipments"]:
        assert item["Shipping Mode"] == "Standard Class"
        assert item["Market"] == "LATAM"
        assert item["Late_delivery_risk"] == 1

